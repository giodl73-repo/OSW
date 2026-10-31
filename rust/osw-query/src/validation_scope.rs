//! Reuse pure validation results only while the same inputs are immutably borrowed.
//!
//! No result survives Store::load. Other bundles, later loads and workspace
//! operations always validate independently. The guard's borrows prevent the
//! active collections or manifest from changing while results are reusable.
use serde_json::Value;
use std::cell::{Cell, RefCell};
use std::collections::BTreeMap;
use std::marker::PhantomData;

type Collections = BTreeMap<String, Vec<Value>>;
type Outcome = Result<bool, String>;

struct State {
    id: u64,
    collections: usize,
    manifest: usize,
    outcomes: BTreeMap<&'static str, Outcome>,
}

thread_local! {
    static ACTIVE: RefCell<Vec<State>> = const { RefCell::new(Vec::new()) };
    static NEXT_ID: Cell<u64> = const { Cell::new(0) };
}

pub(crate) struct Scope<'a> {
    id: u64,
    _inputs: PhantomData<(&'a Collections, &'a Value)>,
    // A guard must be dropped on the thread whose state it changed.
    _same_thread: PhantomData<std::rc::Rc<()>>,
}

impl<'a> Scope<'a> {
    pub(crate) fn new(collections: &'a Collections, manifest: &'a Value) -> Self {
        let id = NEXT_ID.with(|next| {let id=next.get().checked_add(1).expect("validation scope counter exhausted");next.set(id);id});
        let current = State {
            id,
            collections: collections as *const Collections as usize,
            manifest: manifest as *const Value as usize,
            outcomes: BTreeMap::new(),
        };
        ACTIVE.with(|active| active.borrow_mut().push(current));
        Self { id, _inputs: PhantomData, _same_thread: PhantomData }
    }
}

impl Drop for Scope<'_> {
    fn drop(&mut self) {
        // Removing by identity also handles guards dropped out of order: no
        // later guard can restore a cache whose input borrows already ended.
        ACTIVE.with(|active| active.borrow_mut().retain(|state| state.id != self.id));
    }
}

pub(crate) fn checked(
    collections: &Collections,
    manifest: &Value,
    validator: &'static str,
    validate: impl FnOnce() -> Outcome,
) -> Outcome {
    let collections = collections as *const Collections as usize;
    let manifest = manifest as *const Value as usize;
    let scope = ACTIVE.with(|active| {
        let active = active.borrow();
        active.last().filter(|state| state.collections == collections && state.manifest == manifest)
            .map(|state| (state.id, state.outcomes.get(validator).cloned()))
    });
    if let Some((_,Some(outcome))) = &scope { return outcome.clone(); }
    // Do not hold a RefCell borrow across nested validation calls.
    let outcome = validate();
    ACTIVE.with(|active| {
        if let Some(state) = active.borrow_mut().last_mut()
            .filter(|state| scope.as_ref().is_some_and(|(id,_)| *id == state.id)
                && state.collections == collections && state.manifest == manifest) {
            state.outcomes.insert(validator, outcome.clone());
        }
    });
    outcome
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;
    use std::cell::Cell;

    #[test]
    fn identical_immutable_inputs_validate_once_per_scope_and_namespace() {
        let collections = Collections::new(); let manifest = json!({}); let calls = Cell::new(0);
        let _scope = Scope::new(&collections, &manifest);
        for _ in 0..3 {
            assert_eq!(checked(&collections, &manifest, "a", || {calls.set(calls.get()+1);Ok(true)}),Ok(true));
        }
        assert_eq!(checked(&collections, &manifest, "b", || {calls.set(calls.get()+1);Ok(false)}),Ok(false));
        assert_eq!(calls.get(),2);
    }

    #[test]
    fn other_inputs_and_calls_outside_scope_never_reuse_results() {
        let collections = Collections::new(); let other = Collections::new(); let manifest = json!({}); let other_manifest = json!({}); let calls = Cell::new(0);
        let check = || {calls.set(calls.get()+1);Ok(true)};
        checked(&collections,&manifest,"a",check).unwrap();checked(&collections,&manifest,"a",check).unwrap();
        {let _scope=Scope::new(&collections,&manifest);
            checked(&other,&manifest,"a",check).unwrap();checked(&other,&manifest,"a",check).unwrap();
            checked(&collections,&other_manifest,"a",check).unwrap();checked(&collections,&other_manifest,"a",check).unwrap();}
        assert_eq!(calls.get(),6);
    }

    #[test]
    fn errors_remain_errors_and_are_fresh_after_scope_exit_and_mutation() {
        let collections=Collections::new();let mut manifest=json!({"valid":false});let calls=Cell::new(0);
        {let _scope=Scope::new(&collections,&manifest);
            for _ in 0..2 {assert_eq!(checked(&collections,&manifest,"a",||{calls.set(calls.get()+1);Err("exact refusal".into())}),Err("exact refusal".into()));}}
        manifest["valid"]=json!(true);
        {let _scope=Scope::new(&collections,&manifest);assert_eq!(checked(&collections,&manifest,"a",||{calls.set(calls.get()+1);Ok(manifest["valid"]==true)}),Ok(true));}
        assert_eq!(calls.get(),2);
    }

    #[test]
    fn nested_scope_restores_outer_results_and_nested_validators_do_not_borrow_panic() {
        let collections=Collections::new();let other=Collections::new();let manifest=json!({});
        let _scope=Scope::new(&collections,&manifest);
        assert_eq!(checked(&collections,&manifest,"outer",||{
            checked(&collections,&manifest,"inner",||Ok(true))?;
            {let _nested=Scope::new(&other,&manifest);checked(&other,&manifest,"outer",||Ok(false))?;}
            Ok(true)
        }),Ok(true));
        assert_eq!(checked(&collections,&manifest,"outer",||panic!("Outer result should be retained")),Ok(true));
        assert_eq!(checked(&collections,&manifest,"inner",||panic!("Nested validator result should be retained")),Ok(true));
    }

    #[test]
    fn unwinding_drops_scope_without_leaving_a_successful_result() {
        let collections=Collections::new();let manifest=json!({});
        let result=std::panic::catch_unwind(||{let _scope=Scope::new(&collections,&manifest);checked(&collections,&manifest,"a",||Ok(true)).unwrap();panic!("intentional unwind");});
        assert!(result.is_err());
        assert_eq!(checked(&collections,&manifest,"a",||Err("fresh failure".into())),Err("fresh failure".into()));
    }

    #[test]
    fn out_of_order_guard_drop_cannot_restore_results_for_expired_borrows() {
        let collections=Collections::new();let other=Collections::new();let mut manifest=json!({"valid":true});
        let outer=Scope::new(&collections,&manifest);
        checked(&collections,&manifest,"a",||Ok(true)).unwrap();
        let inner=Scope::new(&other,&manifest);
        drop(outer);drop(inner);
        manifest["valid"]=json!(false);
        assert_eq!(checked(&collections,&manifest,"a",||Ok(manifest["valid"]==true)),Ok(false));
    }
}

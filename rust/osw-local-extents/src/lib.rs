//! Dedicated research-query target; shares source with the atlas query engine.
#[path = "../../osw-query/src/local_extents.rs"]
pub mod local_extents;
#[path = "../../osw-query/src/scalar_query.rs"]
mod scalar_query;

#[cfg(target_arch = "wasm32")]
mod wasm {
    use super::local_extents::{EXPECTED_BYTES, LocalExtentStore, MAX_REQUEST_BYTES};
    use serde_json::{Value, json};
    use std::cell::RefCell;
    thread_local! {
        static STORE:RefCell<Option<LocalExtentStore>>=const{RefCell::new(None)};
        static RESULT:RefCell<Vec<u8>>=const{RefCell::new(Vec::new())};
    }
    fn output(value: Value) {
        RESULT.with(|r| *r.borrow_mut() = serde_json::to_vec(&value).unwrap());
    }
    #[unsafe(no_mangle)]
    pub extern "C" fn osw_alloc(len: usize) -> *mut u8 {
        Box::into_raw(vec![0u8; len].into_boxed_slice()) as *mut u8
    }
    #[unsafe(no_mangle)]
    pub unsafe extern "C" fn osw_dealloc(ptr: *mut u8, len: usize) {
        unsafe {
            drop(Box::from_raw(std::ptr::slice_from_raw_parts_mut(ptr, len)));
        }
    }
    #[unsafe(no_mangle)]
    pub extern "C" fn osw_result_ptr() -> *const u8 {
        RESULT.with(|r| r.borrow().as_ptr())
    }
    #[unsafe(no_mangle)]
    pub extern "C" fn osw_result_len() -> usize {
        RESULT.with(|r| r.borrow().len())
    }
    #[unsafe(no_mangle)]
    pub unsafe extern "C" fn osw_local_extents_load(ptr: *const u8, len: usize) -> i32 {
        STORE.with(|s| *s.borrow_mut() = None);
        if len != EXPECTED_BYTES {
            output(json!({"ok":false,"error":"Unexpected local-extent research snapshot size"}));
            return 0;
        }
        let bytes = unsafe { std::slice::from_raw_parts(ptr, len) };
        match LocalExtentStore::load(bytes) {
            Ok(store) => {
                output(store.metadata());
                STORE.with(|s| *s.borrow_mut() = Some(store));
                1
            }
            Err(error) => {
                output(json!({"ok":false,"error":error}));
                0
            }
        }
    }
    #[unsafe(no_mangle)]
    pub extern "C" fn osw_local_extents_metadata() {
        output(
            STORE
                .with(|s| s.borrow().as_ref().map(|s| s.metadata()))
                .unwrap_or_else(|| json!({"ok":false,"error":"Local-extent store not loaded"})),
        );
    }
    fn request(bytes: &[u8], record: bool) -> Value {
        let result = STORE.with(|s| {
            s.borrow()
                .as_ref()
                .ok_or_else(|| "Local-extent store not loaded".to_owned())
                .and_then(|s| {
                    if record {
                        s.record(bytes)
                    } else {
                        s.query(bytes)
                    }
                })
        });
        result.unwrap_or_else(|error| json!({"ok":false,"error":error}))
    }
    #[unsafe(no_mangle)]
    pub unsafe extern "C" fn osw_local_extents_query(ptr: *const u8, len: usize) {
        if len > MAX_REQUEST_BYTES {
            output(json!({"ok":false,"error":"Local-extent query is too large"}));
            return;
        }
        output(request(
            unsafe { std::slice::from_raw_parts(ptr, len) },
            false,
        ));
    }
    #[unsafe(no_mangle)]
    pub unsafe extern "C" fn osw_local_extents_record(ptr: *const u8, len: usize) {
        if len > MAX_REQUEST_BYTES {
            output(json!({"ok":false,"error":"Local-extent record request is too large"}));
            return;
        }
        output(request(
            unsafe { std::slice::from_raw_parts(ptr, len) },
            true,
        ));
    }
}

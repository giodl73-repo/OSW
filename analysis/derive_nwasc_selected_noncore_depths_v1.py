"""Extract only explicit source-specific non-core prose extents, in cloud."""
import copy,hashlib,json,re,xml.etree.ElementTree as ET


def extract_paragraph(text):
    si=list(re.finditer(r'non-core area\b[^.]*?(\d+) m isobath[^.]*?down to (\d+) m',text))
    gi=list(re.finditer(r'core and non-core\b[^.]*?down to (\d+) and (\d+) m respectively[^.]*?(\d+) m isobath',text))
    core=list(re.finditer(r'wedge-shaped\b[^.]*?depth of (\d+) m',text))
    if len(si)!=1 or len(gi)!=1 or len(core)!=1:raise ValueError('One explicit original SI/GI non-core statement required')
    return [{'section_id':'svinoy','reported_noncore_lower_extent_m':int(si[0][2]),'source_core_lower_extent_m':int(core[0][1]),'shoreward_isobath_gate_m':int(si[0][1])},{'section_id':'gimsoy','reported_noncore_lower_extent_m':int(gi[0][2]),'source_core_lower_extent_m':int(gi[0][1]),'shoreward_isobath_gate_m':int(gi[0][3])}]


def audit_and_derive(root,op):
    read=lambda f:json.loads((root/f).read_bytes());context=read(op['source_context_file']);custody=read(context['acquisition_file'])
    if context['schema']!='osw.nwasc-selected-noncore-depth-source-context.v1' or context['entity_id']!='current:norwegian-atlantic-slope' or context['primary_prose_and_figure_visually_reviewed'] is not True or context['source_population_role']!='non_core_selected_Atlantic_Water':raise ValueError('Known separately owned selected non-core context required')
    for f in [context['source_xml_file'],context['source_pdf_file']]:
        meta=next(x for x in custody['files'] if x['path']==f);raw=(root/f).read_bytes()
        if len(raw)!=meta['bytes'] or hashlib.sha256(raw).hexdigest()!=meta['sha256']:raise ValueError('Original publisher XML/PDF custody changed')
    tree=ET.fromstring((root/context['source_xml_file']).read_bytes());paragraphs=[' '.join(''.join(el.itertext()).split()) for el in tree.iter() if el.tag.split('}')[-1]=='p'];candidates=[(i,t) for i,t in enumerate(paragraphs) if 'core is wedge-shaped' in t]
    if len(candidates)!=1:raise ValueError('Unique original spatial-extent paragraph required')
    i,text=candidates[0];extracted=extract_paragraph(text);base=read(op['base_reference_file']);records=[]
    if context['source_mean_definition_years']!=[1993,2022] or context['selection']!={'absolute_salinity_minimum_g_kg':35.16,'absolute_salinity_comparator':'>=','upper_selection_depth_m':50,'core_transport_fraction':.5,'core_selector':'decreasing_absolute_geostrophic_velocity_until50percent_mean_selected_AW_transport','noncore_selector':'remaining_selected_AW_population_outside_core','time_basis':'static_1993_2022_mean_defined_selection'}:raise ValueError('Static source population selection cannot be changed')
    if [s['id'] for s in context['sections']]!=['svinoy','gimsoy']:raise ValueError('Only explicitly resolved SI/GI non-core extents permitted')
    for row,section in zip(extracted,context['sections']):
        old=next(r for r in base['evidence'] if r['id']==section['existing_core_reference_id'])
        if row['section_id']!=section['id'] or row['shoreward_isobath_gate_m']!=section['shoreward_isobath_gate_m'] or old['entity_id']!=context['entity_id'] or old['metric']!='core_lower_boundary_depth' or old['approximate_value_m']!=row['source_core_lower_extent_m'] or row['reported_noncore_lower_extent_m']<=row['source_core_lower_extent_m']:raise ValueError('Source core/non-core roles,section or selection gates changed')
        records.append({'entity_id':context['entity_id'],**row,'source_figure_panel':section['source_figure_panel'],'existing_core_reference_id':old['id'],'source_xml_file':context['source_xml_file'],'source_xml_paragraph_index':i,'source_xml_normalized_paragraph_sha256':hashlib.sha256(text.encode()).hexdigest(),'source_population_role':context['source_population_role'],'source_selection':copy.deepcopy(context['selection']),'source_mean_definition_years':context['source_mean_definition_years']})
    return {'schema':'osw.nwasc-selected-noncore-depth-source-report.v1','records':records,'source_context_file':op['source_context_file'],'source_context_sha256':hashlib.sha256((root/op['source_context_file']).read_bytes()).hexdigest(),'curated_transects_obtained':False,'physical_current_bottom_established':False,'new_ocean_field_requests':0,'runtime_changed':False,'full_goal_complete':False}

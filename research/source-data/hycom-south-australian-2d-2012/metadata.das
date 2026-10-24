Attributes {
    depth {
        String long_name "Depth";
        String standard_name "depth";
        String units "m";
        String positive "down";
        String axis "Z";
        Int32 NAVO_code 5;
    }
    lat {
        String long_name "Latitude";
        String standard_name "latitude";
        String units "degrees_north";
        String point_spacing "even";
        String axis "Y";
        Int32 NAVO_code 1;
    }
    lon {
        String long_name "Longitude";
        String standard_name "longitude";
        String units "degrees_east";
        String point_spacing "even";
        String modulo "360 degrees";
        String axis "X";
        Int32 NAVO_code 2;
    }
    time {
        String long_name "Valid Time";
        String units "hours since 2000-01-01 00:00:00";
        String time_origin "2000-01-01 00:00:00";
        String calendar "gregorian";
        String axis "T";
        Int32 NAVO_code 13;
    }
    tau {
        String long_name "Tau";
        String units "hours since analysis";
        String time_origin "1994-12-30 00:00:00";
        Int32 NAVO_code 56;
    }
    water_u {
        String _CoordinateAxes "time depth lat lon ";
        String long_name "Eastward Water Velocity";
        String standard_name "eastward_sea_water_velocity";
        String units "m/s";
        Int16 _FillValue -30000;
        Int16 missing_value -30000;
        Float32 scale_factor 0.001;
        Float32 add_offset 0.0;
        Int32 NAVO_code 17;
    }
    water_v {
        String _CoordinateAxes "time depth lat lon ";
        String long_name "Northward Water Velocity";
        String standard_name "northward_sea_water_velocity";
        String units "m/s";
        Int16 _FillValue -30000;
        Int16 missing_value -30000;
        Float32 scale_factor 0.001;
        Float32 add_offset 0.0;
        Int32 NAVO_code 18;
    }
    water_temp {
        String _CoordinateAxes "time depth lat lon ";
        String long_name "Water Temperature";
        String standard_name "sea_water_temperature";
        String units "degC";
        Int16 _FillValue -30000;
        Int16 missing_value -30000;
        Float32 scale_factor 0.001;
        Float32 add_offset 20.0;
        Int32 NAVO_code 15;
    }
    salinity {
        String _CoordinateAxes "time depth lat lon ";
        String long_name "Salinity";
        String standard_name "sea_water_salinity";
        String units "psu";
        Int16 _FillValue -30000;
        Int16 missing_value -30000;
        Float32 scale_factor 0.001;
        Float32 add_offset 20.0;
        Int32 NAVO_code 16;
    }
    surf_el {
        String _CoordinateAxes "time lat lon ";
        String long_name "Water Surface Elevation";
        String standard_name "sea_surface_elevation";
        String units "m";
        Int16 _FillValue -30000;
        Int16 missing_value -30000;
        Float32 scale_factor 0.001;
        Float32 add_offset 0.0;
        Int32 NAVO_code 32;
    }
    NC_GLOBAL {
        String classification_level "UNCLASSIFIED";
        String distribution_statement "Approved for public release. Distribution unlimited.";
        String downgrade_date "not applicable";
        String classification_authority "not applicable";
        String institution "Naval Oceanographic Office";
        String source "HYCOM archive file";
        String history "archv2ncdf3z";
        String field_type "instantaneous";
        String Conventions "CF-1.0 NAVO_netcdf_v1.0";
    }
}

-- Orthanc Lua script to assign labels based on DICOM StationName tag (0008,1010) or calling AET
-- This script maps multiple StationNames and AETs to a single label

-- Configuration: Map StationName values and calling AETs to labels
-- Format: ["STATION_NAME_OR_AET"] = "label_name"
local stationname_to_label_mapping = {
    ["FNHC"] = "FNHC",
}

-- Default label for unknown StationNames and AETs (set to nil to not assign any label)
local default_label = "TO-BE-DEFINED"

-- Function to make a valid label by replacing invalid characters
function makeValidLabel(input)
    if input == nil or input == "" then
        return "empty"
    end
    local invalidCharacters = "[^%w_-]"   -- everything that is not alphanumeric or _ or -
    return input:gsub(invalidCharacters, "-")
end

-- Function to get the appropriate label for a StationName or AET
function getLabelForSource(sourceValue)
    if sourceValue == nil or sourceValue == "" then
        return nil
    end

    -- Check if we have a mapping for this source value
    local label = stationname_to_label_mapping[sourceValue]
    if label ~= nil then
        return label
    else
        return nil
    end
end

-- Main callback function triggered when a new instance is stored
function OnStoredInstance(instanceId, tags, metadata, origin)
    print("OnStoredInstance processing instance: " .. instanceId)

    -- Get the StationName from DICOM tags (0008,1010)
    local stationName = tags["StationName"]
    local callingAET = nil
    local label = nil
    local source = "unknown"

    -- Get the calling AET from the origin information if available
    if origin ~= nil and origin["RequestOrigin"] == "DicomProtocol" and origin["RemoteAet"] ~= nil then
        callingAET = origin["RemoteAet"]
        print("Found calling AET: '" .. callingAET .. "'")
    end

    -- First, try to get label from StationName
    if stationName ~= nil and stationName ~= "" then
        print("Found StationName: '" .. stationName .. "'")
        label = getLabelForSource(stationName)
        if label ~= nil then
            source = "StationName"
        end
    end

    -- If no label found from StationName, try calling AET as fallback
    if label == nil and callingAET ~= nil then
        print("StationName not mapped, trying calling AET: '" .. callingAET .. "'")
        label = getLabelForSource(callingAET)
        if label ~= nil then
            source = "calling AET"
        end
    end

    -- If still no label found, use default label
    if label == nil then
        if default_label ~= nil then
            label = default_label
            source = "default"
        end
    end

    -- Apply the label if we have one
    if label ~= nil and label ~= "" then
        print("Mapping " .. source .. " '" .. (stationName or callingAET or "unknown") .. "' to label '" .. label .. "'")

        -- Get the parent study
        local parentStudy = ParseJson(RestApiGet("/instances/" .. instanceId .. "/study"))

        -- Only add label if the study doesn't already have labels (to avoid duplicates)
        if #parentStudy.Labels == 0 then
            print("Adding labels to parent study: " .. parentStudy.ID)

            -- Add the mapped label
            local validLabel = makeValidLabel(label)
            RestApiPut("/studies/" .. parentStudy.ID .. "/labels/" .. validLabel, '')
            print("Added label: " .. validLabel)

        else
            print("Study already has labels, skipping to avoid duplicates")
        end
    else
        print("No label mapping found for StationName '" .. (stationName or "nil") .. "' or calling AET '" .. (callingAET or "nil") .. "'")
    end

    print("OnStoredInstance ... done")
end


-- Initialize the script
print("LUA: StationName/AET-based labeling script loaded")
print("LUA: Configured mappings for " .. #stationname_to_label_mapping .. " StationNames/AETs")
if default_label ~= nil then
    print("LUA: Default label for unknown/missing StationNames and AETs: '" .. default_label .. "'")
else
    print("LUA: No default label configured for unknown/missing StationNames and AETs")
end

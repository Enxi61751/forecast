package com.citicup.dto.agent;

import com.fasterxml.jackson.annotation.JsonAnyGetter;
import com.fasterxml.jackson.annotation.JsonAnySetter;

import java.util.LinkedHashMap;
import java.util.Map;

public class Stage2SingleResponse {

    private final Map<String, Object> fields = new LinkedHashMap<>();

    @JsonAnySetter
    public void putField(String key, Object value) {
        fields.put(key, value);
    }

    @JsonAnyGetter
    public Map<String, Object> getFields() {
        return fields;
    }

    public Object get(String key) {
        return fields.get(key);
    }

    public boolean containsKey(String key) {
        return fields.containsKey(key);
    }

    public Map<String, Object> asMap() {
        return fields;
    }
}
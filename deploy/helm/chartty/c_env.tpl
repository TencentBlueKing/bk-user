{{/* vim: set filetype=mustache: */}}

{{/* Create envs */}}
{{- define "chartty.envs" -}}
{{- with .Values.extrasEnv }}
{{- /* 直接渲染 extrasEnv */ -}}
{{- toYaml . }}
{{- end }}
{{- /* 渲染 sharedUrlEnvMap */ -}}
{{- range $k, $v := .Values.sharedUrlEnvMap }}
{{- if hasKey $.Values.env $k }}
{{- else }}
- name: {{ $k }}
  value: "{{ tpl $v $ }}"
{{- end }}
{{- end }}
{{- /* 渲染 global 环境变量时，如果模块已指定直接跳过 */ -}}
{{- range $k, $v := .Values.global.env }}
{{- if hasKey $.Values.env $k }}
{{- else }}
- name: {{ $k }}
  value: "{{ $v }}"
{{- end }}
{{- end }}
{{- /* 高优先级渲染 .Values.env */ -}}
{{- range $k, $v := .Values.env }}
- name: {{ $k }}
  value: "{{ $v }}"
{{- end }}
{{- end }}
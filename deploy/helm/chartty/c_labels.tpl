{{/* vim: set filetype=mustache: */}}

{{/*
Common labels
*/}}
{{- define "chartty.labels" -}}
helm.sh/chart: {{ include "chartty.chart" . }}
{{- with .Values.podLabels }}
{{ toYaml . }}
{{- end }}
{{ include "chartty.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "chartty.selectorLabels" -}}
app.kubernetes.io/name: {{ include "chartty.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
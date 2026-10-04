# Task 4 Step 2 (continued): known classes behind the false-Unknown alarms

## 40f: where the false-Unknown alarms come from (Worms + Shellcode held out, threshold at 5%, mean over 5 seeds)

`flagged` = share of the class's known flows flagged Unknown; `of alarms` = the class's share of all false alarms. thr / cal = the two validation halves, test = official test.

**entropy**

| known class | flows (test) | flagged: thr | cal | test | of alarms: thr | cal | test |
|---|---|---|---|---|---|---|---|
| Analysis | 438 | 0.414 | 0.334 | 0.205 | 0.177 | 0.128 | 0.063 |
| Backdoor | 345 | 0.434 | 0.421 | 0.176 | 0.226 | 0.187 | 0.043 |
| DoS | 1694 | 0.160 | 0.117 | 0.121 | 0.133 | 0.117 | 0.151 |
| Exploits | 7590 | 0.035 | 0.027 | 0.035 | 0.140 | 0.159 | 0.194 |
| Fuzzers | 4810 | 0.047 | 0.050 | 0.046 | 0.153 | 0.189 | 0.162 |
| Generic | 3418 | 0.027 | 0.041 | 0.030 | 0.024 | 0.051 | 0.078 |
| Normal | 33832 | 0.005 | 0.004 | 0.009 | 0.036 | 0.042 | 0.224 |
| Reconnaissance | 2469 | 0.068 | 0.073 | 0.047 | 0.115 | 0.136 | 0.085 |

**msp**

| known class | flows (test) | flagged: thr | cal | test | of alarms: thr | cal | test |
|---|---|---|---|---|---|---|---|
| Analysis | 438 | 0.207 | 0.271 | 0.099 | 0.087 | 0.098 | 0.013 |
| Backdoor | 345 | 0.201 | 0.219 | 0.108 | 0.104 | 0.089 | 0.012 |
| DoS | 1694 | 0.177 | 0.132 | 0.127 | 0.135 | 0.113 | 0.067 |
| Exploits | 7590 | 0.063 | 0.052 | 0.057 | 0.245 | 0.247 | 0.136 |
| Fuzzers | 4810 | 0.060 | 0.057 | 0.066 | 0.194 | 0.198 | 0.098 |
| Generic | 3418 | 0.036 | 0.035 | 0.040 | 0.027 | 0.047 | 0.043 |
| Normal | 33832 | 0.024 | 0.021 | 0.057 | 0.167 | 0.161 | 0.599 |
| Reconnaissance | 2469 | 0.030 | 0.033 | 0.043 | 0.047 | 0.056 | 0.033 |

## 45f: where the false-Unknown alarms come from (Worms + Shellcode held out, threshold at 5%, mean over 5 seeds)

`flagged` = share of the class's known flows flagged Unknown; `of alarms` = the class's share of all false alarms. thr / cal = the two validation halves, test = official test.

**entropy**

| known class | flows (test) | flagged: thr | cal | test | of alarms: thr | cal | test |
|---|---|---|---|---|---|---|---|
| Analysis | 438 | 0.454 | 0.417 | 0.270 | 0.184 | 0.148 | 0.068 |
| Backdoor | 345 | 0.448 | 0.531 | 0.285 | 0.219 | 0.204 | 0.060 |
| DoS | 1694 | 0.194 | 0.155 | 0.145 | 0.158 | 0.130 | 0.152 |
| Exploits | 7590 | 0.036 | 0.029 | 0.036 | 0.138 | 0.150 | 0.171 |
| Fuzzers | 4810 | 0.041 | 0.050 | 0.072 | 0.130 | 0.148 | 0.216 |
| Generic | 3418 | 0.047 | 0.085 | 0.028 | 0.039 | 0.070 | 0.062 |
| Normal | 33832 | 0.002 | 0.003 | 0.009 | 0.015 | 0.019 | 0.199 |
| Reconnaissance | 2469 | 0.076 | 0.089 | 0.047 | 0.124 | 0.145 | 0.071 |

**msp**

| known class | flows (test) | flagged: thr | cal | test | of alarms: thr | cal | test |
|---|---|---|---|---|---|---|---|
| Analysis | 438 | 0.313 | 0.335 | 0.196 | 0.135 | 0.116 | 0.031 |
| Backdoor | 345 | 0.319 | 0.380 | 0.220 | 0.156 | 0.141 | 0.028 |
| DoS | 1694 | 0.199 | 0.151 | 0.142 | 0.159 | 0.127 | 0.087 |
| Exploits | 7590 | 0.054 | 0.047 | 0.050 | 0.211 | 0.217 | 0.137 |
| Fuzzers | 4810 | 0.049 | 0.052 | 0.101 | 0.153 | 0.163 | 0.176 |
| Generic | 3418 | 0.030 | 0.055 | 0.033 | 0.025 | 0.042 | 0.041 |
| Normal | 33832 | 0.009 | 0.013 | 0.038 | 0.082 | 0.101 | 0.461 |
| Reconnaissance | 2469 | 0.055 | 0.071 | 0.044 | 0.084 | 0.102 | 0.038 |

## 48f: where the false-Unknown alarms come from (Worms + Shellcode held out, threshold at 5%, mean over 5 seeds)

`flagged` = share of the class's known flows flagged Unknown; `of alarms` = the class's share of all false alarms. thr / cal = the two validation halves, test = official test.

**iforest+entropy:max**

| known class | flows (test) | flagged: thr | cal | test | of alarms: thr | cal | test |
|---|---|---|---|---|---|---|---|
| Analysis | 438 | 0.238 | 0.217 | 0.116 | 0.109 | 0.066 | 0.029 |
| Backdoor | 345 | 0.266 | 0.313 | 0.149 | 0.140 | 0.112 | 0.030 |
| DoS | 1694 | 0.157 | 0.117 | 0.117 | 0.132 | 0.115 | 0.115 |
| Exploits | 7590 | 0.049 | 0.047 | 0.043 | 0.194 | 0.263 | 0.183 |
| Fuzzers | 4810 | 0.037 | 0.048 | 0.048 | 0.126 | 0.141 | 0.128 |
| Generic | 3418 | 0.073 | 0.116 | 0.113 | 0.100 | 0.097 | 0.188 |
| Normal | 33832 | 0.017 | 0.012 | 0.016 | 0.143 | 0.147 | 0.289 |
| Reconnaissance | 2469 | 0.043 | 0.060 | 0.027 | 0.075 | 0.078 | 0.038 |

**msp**

| known class | flows (test) | flagged: thr | cal | test | of alarms: thr | cal | test |
|---|---|---|---|---|---|---|---|
| Analysis | 438 | 0.310 | 0.344 | 0.206 | 0.134 | 0.120 | 0.033 |
| Backdoor | 345 | 0.328 | 0.392 | 0.241 | 0.161 | 0.148 | 0.031 |
| DoS | 1694 | 0.206 | 0.159 | 0.142 | 0.166 | 0.130 | 0.088 |
| Exploits | 7590 | 0.053 | 0.044 | 0.046 | 0.205 | 0.202 | 0.127 |
| Fuzzers | 4810 | 0.049 | 0.047 | 0.102 | 0.150 | 0.155 | 0.182 |
| Generic | 3418 | 0.032 | 0.056 | 0.034 | 0.024 | 0.056 | 0.044 |
| Normal | 33832 | 0.009 | 0.013 | 0.038 | 0.081 | 0.099 | 0.457 |
| Reconnaissance | 2469 | 0.054 | 0.068 | 0.045 | 0.084 | 0.102 | 0.039 |


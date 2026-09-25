import base64, os;

def w(p, c):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, " wb\) as f: f.write(base64.b64decode(c))

# Registry
reg = \aW1wb3J0IG9zCmltcG9ydCBqb2JsaWIKZnJvbSBkYXRldGltZSBpbXBvcnQgZGF0ZXRpbWUKZnJvbSBwYXRobGliIGltcG9ydB BajBhdC4gS2V5Cg==\ # placeholder

w(\api_tcc/ia/model_registry.py\, reg)

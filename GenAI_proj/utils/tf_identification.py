from __future__ import annotations

import json
from pathlib import Path
from io import BytesIO
from PIL import Image

# Import TensorFlow if available
try:
    import tensorflow as tf
    from tensorflow.keras.applications.resnet50 import preprocess_input
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    preprocess_input = None

# Import frontend categories to validate output
from data.mock_data import IDENTIFY_CATEGORIES

# Model class to frontend category mapping
CLASS_MAPPING = {
    "Battery": "Battery",
    "Keyboard": "Small Appliance",
    "Microwave": "Small Appliance",
    "Mobile": "Phone",
    "Mouse": "Small Appliance",
    "PCB": "Small Appliance",
    "Player": "Small Appliance",
    "Printer": "Small Appliance",
    "Television": "Small Appliance",
    "Washing Machine": "Small Appliance",
}

MODEL_PATH = Path(__file__).parent.parent / "models" / "ewaste_model.keras"
CLASS_INDICES_PATH = Path(__file__).parent.parent / "models" / "class_indices.json"

def _load_class_indices():
    if CLASS_INDICES_PATH.exists():
        try:
            with open(CLASS_INDICES_PATH, "r") as f:
                return json.load(f)
        except:
            pass
    # Default minimal set for fallback
    return {"Battery": 0, "Mobile": 3, "Printer": 7}

# Valid frontend categories from model
MODEL_FRONTEND_CATEGORIES = {"Phone", "Battery", "Small Appliance"}

def _load_model():
    if not TF_AVAILABLE or not MODEL_PATH.exists():
        return None
    try:
        return tf.keras.models.load_model(MODEL_PATH)
    except:
        return None

_model = None
_class_indices = None

def _get_model():
    global _model
    if _model is None:
        _model = _load_model()
    return _model

def _get_class_indices():
    global _class_indices
    if _class_indices is None:
        _class_indices = _load_class_indices()
    return _class_indices

def _preprocess_image(image):
    if image.mode != "RGB":
        image = image.convert("RGB")
    return image.resize((224, 224), Image.Resampling.LANCZOS)

def predict_from_image(data, filename="", hint=""):
    model = _get_model()
    class_indices = _get_class_indices()
    idx_to_class = {v: k for k, v in class_indices.items()}
    
    if model is None:
        # Fallback to mock classifier
        return _mock_predict(data, filename, hint)
    
    try:
        image = Image.open(BytesIO(data))
        image = _preprocess_image(image)
        img_array = tf.keras.utils.img_to_array(image)
        img_array = tf.expand_dims(img_array, 0)
        img_array = preprocess_input(img_array)
        predictions = model.predict(img_array, verbose=0)[0]
        # The model's output layer already has softmax activation, so predictions are already probabilities:
        # DO NOT call tf.nn.softmax(predictions) again as it squashes probabilities into uniform ~0.10!
        if not isinstance(predictions, (list, tuple)):
            try:
                predictions = predictions.numpy()
            except AttributeError:
                pass
        
        top_indices = predictions.argsort()[-3:][::-1]
        predictions_list = []
        for idx in top_indices:
            class_name = idx_to_class.get(idx, f"Class_{idx}")
            confidence = float(predictions[idx])
            frontend_cat = CLASS_MAPPING.get(class_name, class_name)
            predictions_list.append({
                "category": frontend_cat,
                "label": class_name,
                "confidence": round(confidence, 4),
            })
        
        top_class = idx_to_class.get(top_indices[0], "Mobile")
        frontend_top = CLASS_MAPPING.get(top_class, "Small Appliance")
        confidence = float(predictions[top_indices[0]])
        
        # Ensure frontend category is valid for frontend UI
        # If model class doesn't map to a frontend category, use Small Appliance
        if frontend_top not in IDENTIFY_CATEGORIES:
            frontend_top = "Small Appliance"
        
        # Keyword hint boost
        if hint:
            lowered = hint.lower()
            if "phone" in lowered and frontend_top == "Phone":
                confidence = min(0.99, confidence + 0.05)
            elif "battery" in lowered and frontend_top == "Battery":
                confidence = min(0.99, confidence + 0.05)
        
        return {
            "device": frontend_top,
            "detected_device": top_class,
            "confidence": round(confidence, 4),
            "predictions": predictions_list,
            "needs_review": confidence < 0.75,
            "method": "tensorflow",
            "source": filename or "camera capture",
            "hint_matched": hint if hint else None,
        }
    except:
        return _mock_predict(data, filename, hint)

def _mock_predict(data, filename, hint):
    from utils.identification import predict_from_image as mock_predict
    return mock_predict(data, filename, hint)

def manual_identification(category):
    return {
        "device": category,
        "confidence": 1.0,
        "predictions": [{"category": category, "confidence": 1.0}],
        "needs_review": False,
        "method": "manual",
        "source": "manual selection",
    }

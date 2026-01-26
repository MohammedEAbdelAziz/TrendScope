
import shutil
from pathlib import Path
from optimum.onnxruntime import ORTQuantizer, ORTModelForSequenceClassification
from optimum.onnxruntime.configuration import AutoQuantizationConfig

def build_quantized_model():
    """Download, convert, and quantize the financial sentiment model"""
    model_id = "mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis"
    output_dir = Path("model_quantized")
    
    print(f"Downloading and converting {model_id} to ONNX...")
    # Load model from Hub and export to ONNX
    model = ORTModelForSequenceClassification.from_pretrained(
        model_id, 
        export=True
    )
    
    # Define quantization configuration (AVX2 optimized for CPU)
    # is_static=False -> Dynamic Quantization (better for NLP)
    qconfig = AutoQuantizationConfig.avx2(is_static=False, per_channel=False)
    
    # Create quantizer
    quantizer = ORTQuantizer.from_pretrained(model)
    
    # Apply quantization
    print("Applying dynamic quantization (Int8)...")
    quantizer.quantize(
        save_dir=output_dir,
        quantization_config=qconfig,
    )
    
    # Clean up the intermediate full-precision model to save space
    # The quantizer saves 'model_quantized.onnx'. We might have a 'model.onnx' if export saved it there
    # ORTModelForSequenceClassification.from_pretrained(export=True) saves to a temp spot or the object holds it
    # Actually, let's verify where it saves. 
    # Usually it doesn't save to disk until .save_pretrained is called, 
    # but quantizer.from_pretrained(model) uses the model object.
    # The quantizer.quantize save_dir will contain 'model_quantized.onnx'.
    # Note: ORTModel export usually happens to a cache or temp unless specified.
    
    print(f"Model saved to {output_dir}")
    
    # Verify file existence
    if (output_dir / "model_quantized.onnx").exists():
        print("✅ Quantized model created successfully.")
        
        # Remove the 'model.onnx' if it exists in the output dir (some versions might save it)
        full_precision_path = output_dir / "model.onnx"
        if full_precision_path.exists():
            print("Cleaning up full-precision model...")
            full_precision_path.unlink()
    else:
        print("❌ Error: Quantized model not found.")

if __name__ == "__main__":
    build_quantized_model()

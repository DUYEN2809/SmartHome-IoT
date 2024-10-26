import google.generativeai as genai

class GeminiAPI:
  """
  Lớp này cung cấp các phương thức để tương tác với Gemini API.
  """
  def __init__(self, api_key_path="D://api_key.txt"):
    """
    Khởi tạo đối tượng GeminiAPI.

    Args:
      api_key_path: Đường dẫn đến file chứa API key.
      model_name: Tên của mô hình Gemini đã được finetuning.
    """
    with open(api_key_path, "r") as f:
      self.api_key = f.read().strip()
    genai.configure(api_key=self.api_key)
    self.model = genai.GenerativeModel(model_name="tunedModels/training-lmlhujmzb41w")

  def call_api(self, prompt):
    """
    Tạo văn bản bằng cách sử dụng mô hình Gemini.

    Args:
      prompt: Đầu vào cho mô hình.

    Returns:
      Kết quả được tạo bởi mô hình.
    """
    response = self.model.generate_content(prompt)
    return response.text

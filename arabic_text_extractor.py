import pdfplumber
import requests
from bs4 import BeautifulSoup
import arabic_reshaper
from bidi.algorithm import get_display

class ArabicTextExtractor:
    """
    فئة لاستخراج النصوص العربية من مصادر مختلفة مثل ملفات PDF ومواقع الويب
    """
    
    @staticmethod
    def extract_from_pdf(pdf_path):
        """
        استخراج النص العربي من ملف PDF
        
        المعلمات:
            pdf_path (str): المسار إلى ملف PDF
            
        العائد:
            str: النص المستخرج
        """
        try:
            extracted_text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        extracted_text += text + "\n\n"
            
            return extracted_text
        except Exception as e:
            print(f"حدث خطأ أثناء استخراج النص من ملف PDF: {e}")
            return ""
    
    @staticmethod
    def extract_from_url(url):
        """
        استخراج النص العربي من موقع ويب
        
        المعلمات:
            url (str): عنوان URL للموقع
            
        العائد:
            str: النص المستخرج
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers)
            response.encoding = 'utf-8'  # ضمان ترميز UTF-8
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # إزالة العناصر غير المرغوب فيها
            for script in soup(["script", "style"]):
                script.extract()
            
            # استخراج النص
            text = soup.get_text(separator='\n')
            
            # تنظيف النص
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            return text
        except Exception as e:
            print(f"حدث خطأ أثناء استخراج النص من الموقع: {e}")
            return ""
    
    @staticmethod
    def reshape_arabic_text(text):
        """
        إعادة تشكيل النص العربي لعرضه بشكل صحيح
        
        المعلمات:
            text (str): النص العربي الأصلي
            
        العائد:
            str: النص العربي المعاد تشكيله
        """
        try:
            reshaped_text = arabic_reshaper.reshape(text)
            bidi_text = get_display(reshaped_text)
            return bidi_text
        except Exception as e:
            print(f"حدث خطأ أثناء إعادة تشكيل النص العربي: {e}")
            return text
    
    @staticmethod
    def fix_pdf_text_direction(text):
        """
        تصحيح اتجاه النص العربي المستخرج من ملفات PDF
        
        المعلمات:
            text (str): النص المستخرج من ملف PDF
            
        العائد:
            str: النص بعد تصحيح الاتجاه
        """
        try:
            # تقسيم النص إلى أسطر
            lines = text.split('\n')
            corrected_lines = []
            
            for line in lines:
                # التحقق مما إذا كان السطر يحتوي على نص عربي
                if any('\u0600' <= c <= '\u06FF' for c in line):
                    # تقسيم السطر إلى كلمات
                    words = line.split()
                    # عكس ترتيب الكلمات للنص العربي
                    words.reverse()
                    corrected_line = ' '.join(words)
                    corrected_lines.append(corrected_line)
                else:
                    corrected_lines.append(line)
            
            # إعادة تجميع النص
            corrected_text = '\n'.join(corrected_lines)
            return corrected_text
        except Exception as e:
            print(f"حدث خطأ أثناء تصحيح اتجاه النص: {e}")
            return text

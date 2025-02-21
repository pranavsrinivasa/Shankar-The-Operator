import cv2
import numpy as np
import pytesseract
import xml.etree.ElementTree as ET
import pyautogui

# IN CASE THAT YOU HAVE WINDOWS MACHINE ELSE COMMENT IT 
pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract.exe'
import time

class stx:
    def __init__(self,filename = "ui_elements_ocr.xml"):
        self.filename = filename
        pass
    def extract_all_ui_elements_to_xml(self):
        # Capture a screenshot of the current screen
        screenshot = pyautogui.screenshot()
        image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        
        # Increase contrast: Convert to grayscale and apply CLAHE
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        contrast_gray = clahe.apply(gray)
        # Convert back to BGR for annotation purposes
        contrast_image = cv2.cvtColor(contrast_gray, cv2.COLOR_GRAY2BGR)
        
        # Run OCR using pytesseract on the enhanced image to get bounding box details
        data = pytesseract.image_to_data(contrast_image, output_type=pytesseract.Output.DICT)
        
        # Create the XML root element
        root = ET.Element("TextElements")
        
        # Loop over each detected text element
        n_boxes = len(data['level'])
        for i in range(n_boxes):
            text = data['text'][i].strip()
            # Process only non-empty text detections with a valid confidence
            if text != "" and int(data['conf'][i]) > 0:
                x = data['left'][i]
                y = data['top'][i]
                w = data['width'][i]
                h = data['height'][i]
                
                # Draw the bounding box and add the text label
                cv2.rectangle(contrast_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(contrast_image, text, (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                # Create an XML node for this text element
                element = ET.SubElement(root, "Element")
                ET.SubElement(element, "Text").text = text
                ET.SubElement(element, "X").text = str(x + w//2)
                ET.SubElement(element, "Y").text = str(y + h//2)
        
        # Save the XML tree to file
        tree = ET.ElementTree(root)
        tree.write(self.filename, encoding="utf-8", xml_declaration=True)
        print(f"XML file '{self.filename}' created with text coordinates.")
        
        # Display the annotated image with bounding boxes
        cv2.imshow("Detected Text", contrast_image)
        time.sleep(0.2)
        cv2.waitKey(1)
        cv2.destroyAllWindows()

if __name__ == "__main__":
    abc = stx()

    abc.extract_text_coordinates_to_xml()
import xml.etree.ElementTree as ET
import uiautomation as auto
import os, tempfile

class stx:
    def __init__(self,filename = "ui_elements.xml"):
        self.filename = filename
        pass
    def extract_all_ui_elements_to_xml(self):
        root = ET.Element("UIElements")

        # Get all UI elements across the screen (recursive search)
        def scan_elements(element, depth=0):
            """ Recursively scan UI elements and extract their details. """
            if depth > 5:  # Limit recursion depth to avoid excessive scanning
                return

            try:
                element_xml = ET.SubElement(root, "Element")
                ET.SubElement(element_xml, "Name").text = str(element.Name) or "Unknown"
                ET.SubElement(element_xml, "ControlType").text = str(element.ControlType)
                ET.SubElement(element_xml, "X").text = str((element.BoundingRectangle.left + element.BoundingRectangle.right)/2)
                ET.SubElement(element_xml, "Y").text = str((element.BoundingRectangle.top + element.BoundingRectangle.bottom)/2)
                # Recursively scan child elements
                for child in element.GetChildren():
                    scan_elements(child, depth + 1)

            except Exception as e:
                print(f"Error scanning element: {e}")

        # Start scanning from the root (desktop)
        scan_elements(auto.GetRootControl())

        # Save to XML
        tree = ET.ElementTree(root)
        with open(self.filename, "wb") as xml_file:
            tree.write(xml_file)

        print(f"XML file '{self.filename}' created with UI element coordinates.")


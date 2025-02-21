import pyautogui
import keyboard
import time
from PIL import Image
import base64
from io import BytesIO

class Mousepy:
    def __init__(self):
        pass
    
    def mouse_left_click(self):
        pyautogui.leftClick()
        return "Mouse Left Clicked"
    
    def mouse_right_click(self):
        pyautogui.rightClick()
        return "Mouse Right Clicked"

    def mouse_position(self):
        x, y = pyautogui.position()
        pixel_color = pyautogui.screenshot(imageFilename='temp.png').getpixel((x, y))
        return x,y,pixel_color

    def move_mouse_to(self,x, y):
        pyautogui.moveTo(x, y)
        x1,y1,pixel_color = self.mouse_position()
        self.capture_screenshot_with_cursor()
        return f"Mouse moved to ({x1},{y1}) with pixel color = {pixel_color}"

    def track_mouse_position(self,maxtime=5):
        print("Mouse position tracker running...")
        print("Press 'q' to quit")
        record = {}
        try:
            start = time.time()
            end = time.time()
            while True and (end-start) < maxtime:
                x, y = pyautogui.position()
                pixel_color = pyautogui.screenshot().getpixel((x, y))
                record[f'{end-start}'] = (x,y,pixel_color)
                print(f"\rMouse Position: X: {x}, Y: {y} | RGB Color: {pixel_color}", end='')
                if keyboard.is_pressed('q'):
                    print("\nTracking stopped.")
                    break
                time.sleep(0.5)
                end = time.time()
                
        except KeyboardInterrupt:
            print("\nTracking stopped.")

        if len(record.keys()) > 0:
            return record
        else:
            return 'Tracking Failed'
    
    def capture_screenshot_with_cursor(self,*args,**kwargs):
        screenshot = pyautogui.screenshot()
        x, y = pyautogui.position()
        cursor = Image.open('Tools\cursor.png').convert("RGBA")
        cursor = cursor.resize((50,71))
        r, g, b, a = cursor.split()
        red_cursor = Image.merge("RGBA", (r.point(lambda p: 255), g.point(lambda p: 0), b.point(lambda p: 0), a))
        screenshot.paste(red_cursor, (x+1, y+1), red_cursor)
        screenshot.save('temp.png')
        buffered = BytesIO()
        screenshot.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return img_str

if __name__ == "__main__":
    mouse = Mousepy()
    print(mouse.move_mouse_to(177,63))
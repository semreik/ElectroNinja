import os
import re
import time
import logging
import subprocess
import shutil
import psutil
from electroninja.config.settings import Config
import fitz  # PyMuPDF for PDF to image conversion
from PIL import Image
from pywinauto import Application
from pywinauto.keyboard import send_keys  # For global keystroke sending
from electroninja.config.settings import Config

# Set up logging
logger = logging.getLogger('electroninja')

def save_file(content, file_path):
    """
    Save the provided content to the specified file path.
    Overwrites the file if it already exists.
    """
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info(f"File saved to: {file_path}")
    except Exception as e:
        logger.error(f"Failed to save file {file_path}: {e}")

class LTSpiceInterface:
    """
    A simple LTSpice automation interface that:
      1. Opens an ASC file in LTSpice.
      2. Presses Ctrl+P to open the print dialog.
      3. Immediately sends a global Enter keystroke to accept the default printer.
      4. Waits for the Save Print Output As dialog, pastes the desired PDF path, and presses Enter.
      5. Converts the generated PDF to a PNG image and removes the PDF.
    """
    
    def __init__(self, config=None):
        self.config = config or Config()
        self.ltspice_path = self.config.LTSPICE_PATH
        if not os.path.exists(self.ltspice_path):
            logger.warning(f"LTSpice executable not found at '{self.ltspice_path}'")
        else:
            logger.info(f"LTSpice found at '{self.ltspice_path}'")
    
    def process_circuit(self, asc_code_or_path, prompt_id, iteration):
        """
        Process a circuit by:
          - Creating output folders.
          - Writing/copying the ASC file.
          - Closing any running LTSpice instances.
          - Launching LTSpice and automating the print-to-PDF process.
          - Converting the resulting PDF to a PNG image.
          - Removing the temporary PDF.
          
        Returns (asc_path, image_path) on success, or None on failure.
        """
        
        output_dir = self._create_output_folders(prompt_id, iteration)
        asc_path = os.path.join(output_dir, "code.asc")
        pdf_path = os.path.join(output_dir, "code.pdf")
        image_path = os.path.join(output_dir, "image.png")
        
        # Write or copy the ASC file.
        if isinstance(asc_code_or_path, str) and not os.path.isfile(asc_code_or_path):
            self._write_asc(asc_code_or_path, asc_path)
        elif os.path.isfile(asc_code_or_path) and asc_code_or_path != asc_path:
            shutil.copy(asc_code_or_path, asc_path)
            logger.info(f"Copied ASC file from {asc_code_or_path} to {asc_path}")
        
        # Close any running LTSpice processes.
        self._close_ltspice(quiet=True)
        
        # Automate LTSpice to print the circuit to a PDF.
        if not self._run_ltspice_gui_and_print(asc_path, pdf_path):
            logger.error("Failed to automate LTSpice print to PDF.")
            return None
        
        # Convert the PDF to a PNG image.
        if not self._convert_pdf_to_png(pdf_path, image_path):
            logger.error("Failed to convert PDF to PNG.")
            return None
        
        try:
            os.remove(pdf_path)
            logger.info(f"Removed temporary PDF file: {pdf_path}")
        except Exception as e:
            logger.warning(f"Could not remove PDF file: {e}")
        
        logger.info(f"Successfully processed circuit. ASC: {asc_path}, Image: {image_path}")
        return asc_path, image_path
    
    def _wait_for_window(self, app, title_pattern, timeout=3, retry_interval=0.1):
        """
        Wait for a window whose title matches title_pattern.
        """
        start_time = time.time()
        current_retry = retry_interval
        while time.time() - start_time < timeout:
            for win in app.windows():
                if re.search(title_pattern, win.window_text(), re.IGNORECASE):
                    return win
            time.sleep(current_retry)
            current_retry = min(current_retry * 1.5, 0.5)
        available_titles = [w.window_text() for w in app.windows()]
        logger.debug(f"Available window titles: {available_titles}")
        return None
    
    def _wait_for_file_creation(self, file_path, max_wait=15, check_interval=0.2, min_size=10000):
        """
        Wait until the file exists and its size is stable and above a minimum threshold.
        """
        start_time = time.time()
        last_size = 0
        while time.time() - start_time < max_wait:
            if os.path.exists(file_path):
                current_size = os.path.getsize(file_path)
                if current_size >= min_size and current_size == last_size:
                    return True
                last_size = current_size
            time.sleep(check_interval)
        return False
    
    def _close_ltspice(self, quiet=False):
        """
        Close all running LTSpice processes.
        """
        try:
            ltspice_procs = []
            for proc in psutil.process_iter(['pid', 'name']):
                if 'LTspice' in proc.info['name']:
                    ltspice_procs.append(proc.info['pid'])
            if not ltspice_procs:
                if not quiet:
                    logger.info("No LTSpice processes found to close")
                return
            for pid in ltspice_procs:
                try:
                    if not quiet:
                        logger.info(f"Closing LTSpice process: {pid}")
                    psutil.Process(pid).terminate()
                except Exception:
                    pass
            if ltspice_procs:
                time.sleep(0.1)
            for proc in psutil.process_iter(['pid', 'name']):
                if 'LTspice' in proc.info['name']:
                    try:
                        psutil.Process(proc.info['pid']).kill()
                        if not quiet:
                            logger.info(f"Force killed LTSpice process: {proc.info['pid']}")
                    except Exception:
                        pass
        except Exception as e:
            if not quiet:
                logger.warning(f"Error closing LTSpice: {e}")
    
    def _convert_pdf_to_png(self, pdf_path, image_path):
        """
        Convert the first page of the PDF to a PNG image.
        Renders at 3x zoom, crops to the bounding box, centers on a white square,
        and saves with optimization.
        """
        try:
            doc = fitz.open(pdf_path)
            page = doc[0]
            zoom = 3.0
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            pix.save(image_path)
            doc.close()
            
            with Image.open(image_path) as im:
                bbox = im.getbbox()
                if bbox:
                    im_cropped = im.crop(bbox)
                    w, h = im_cropped.size
                    new_h = int(h * 0.90)
                    im_cropped = im_cropped.crop((0, 0, w, new_h))
                    final_size = max(im_cropped.width, im_cropped.height)
                    final_img = Image.new("RGB", (final_size, final_size), "white")
                    offset_x = (final_size - im_cropped.width) // 2
                    offset_y = (final_size - im_cropped.height) // 2
                    final_img.paste(im_cropped, (offset_x, offset_y))
                    final_img.save(image_path, optimize=True, quality=90)
                else:
                    w, h = im.size
                    final_size = max(w, h)
                    final_img = Image.new("RGB", (final_size, final_size), "white")
                    final_img.paste(im, ((final_size - w) // 2, (final_size - h) // 2))
                    final_img.save(image_path, optimize=True, quality=90)
            logger.info(f"Converted PDF to PNG and cropped: {image_path}")
            return True
        except Exception as e:
            logger.error(f"Error converting PDF to PNG: {e}")
            return False
    
    def _create_output_folders(self, prompt_id, iteration):
        """
        Create the output folder structure: {OUTPUT_DIR}/prompt{prompt_id}/output{iteration}
        """
        prompt_dir = os.path.join(self.config.OUTPUT_DIR, f"prompt{prompt_id}")
        os.makedirs(prompt_dir, exist_ok=True)
        output_dir = os.path.join(prompt_dir, f"output{iteration}")
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"Created output structure: {output_dir}")
        return output_dir
    
    def _write_asc(self, asc_code_or_path, asc_path):
        """
        Write the ASC file content to asc_path.
        If asc_code_or_path is a file, read its content; otherwise, use it directly.
        """
        if os.path.isfile(asc_code_or_path):
            with open(asc_code_or_path, "r", encoding="utf-8", errors="replace") as src:
                asc_data = src.read()
        else:
            asc_data = asc_code_or_path
        save_file(asc_data, asc_path)
        logger.info(f"Wrote ASC file: {asc_path}")

    def _run_ltspice_gui_and_print(self, asc_path, pdf_path):
        """
        Automate printing:
          1. Open the ASC file in LTSpice.
          2. Wait for LTSpice to load.
          3. Press Ctrl+P to open the print dialog.
          4. Immediately send a global Enter to accept default printer.
          5. Wait for the Save Print Output As dialog, paste the PDF path, and press Enter.
          6. Wait for the PDF to be generated.
          7. Close LTSpice after PDF generation.
        """
        logger.info(f"Opening LTSpice GUI for {asc_path}")
        proc = None
        try:
            # Launch LTSpice.
            proc = subprocess.Popen([self.ltspice_path, asc_path], shell=False)
            time.sleep(0.1)  # Wait for LTSpice to load
            
            # Connect to LTSpice.
            app = Application().connect(process=proc.pid)
            main_window = app.top_window()
            main_window.set_focus()
            logger.info("Connected to LTSpice and focused main window")
            time.sleep(0.001)
            
            # Step 1: Press Ctrl+P.
            main_window.type_keys("^p", pause=0.001)
            logger.info("Sent Ctrl+P to open print dialog")
            time.sleep(0.001)
            
            # Step 2: Immediately send global Enter to accept default printer.
            send_keys("{ENTER}", pause=0.001)
            logger.info("Sent global Enter to accept default printer")
            time.sleep(0.001)
            
            # Step 3: Wait for the Save Print Output As dialog.
            save_dlg = self._wait_for_window(app, r".*save print output as.*", timeout=10)
            if not save_dlg:
                logger.error("Save dialog not found")
                self._close_ltspice()
                return False
            save_dlg.set_focus()
            logger.info(f"Found save dialog: {save_dlg.window_text()}")
            time.sleep(0.001)
            
            # Step 4: Paste the PDF path.
            save_dlg.type_keys("^a{BACKSPACE}", pause=0.001)
            time.sleep(0.001)
            save_dlg.type_keys(pdf_path, pause=0.001)
            logger.info(f"Pasted PDF path: {pdf_path}")
            time.sleep(0.001)
            
            # Step 5: Press Enter to save PDF.
            save_dlg.type_keys("{ENTER}", pause=0.0001)
            logger.info("Pressed Enter to save PDF")
            time.sleep(4)  # Wait 4 seconds for PDF generation
            
            # Step 6: Now explicitly close LTSpice after PDF generation
            self._close_ltspice(quiet=False)
            logger.info("Closed LTSpice after PDF generation")
            
            # Ensure PDF exists before returning success
            if os.path.exists(pdf_path):
                return True
            else:
                logger.error("PDF file not created after waiting")
                return False
                
        except Exception as e:
            logger.error(f"Error automating LTSpice: {e}")
            if proc:
                try:
                    proc.terminate()
                except:
                    pass
            self._close_ltspice()
            return False
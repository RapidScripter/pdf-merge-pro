import os
from PyPDF2 import PdfMerger
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter
import threading

customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class PDFMergerApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # Configure window
        self.title("PDF Merger App")
        self.geometry(f"{600}x{400}")

        # Configure grid layout (2x2)
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure((0, 1), weight=1)

        # Create source folder selection button
        self.source_folder_button = customtkinter.CTkButton(self, text="Select Source Folder", command=self.select_source_folder)
        self.source_folder_button.grid(row=0, column=0, padx=20, pady=20)

        # Create destination folder selection button
        self.dest_folder_button = customtkinter.CTkButton(self, text="Select Destination Folder", command=self.select_dest_folder)
        self.dest_folder_button.grid(row=0, column=1, padx=20, pady=20)

        # Create progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = customtkinter.CTkProgressBar(self, variable=self.progress_var)
        self.progress_bar.grid(row=1, column=0, columnspan=2, padx=20, pady=20, sticky="ew")

        # Create merge button
        self.merge_button = customtkinter.CTkButton(self, text="Merge PDFs", command=self.merge_pdfs)
        self.merge_button.grid(row=3, column=0, columnspan=2, padx=20, pady=20, sticky="ew")

        # Create merge button for subfolders
        self.merge_subfolders_button = customtkinter.CTkButton(self, text="Merge PDFs from Subfolders", command=self.merge_pdfs_for_subfolders_gui)
        self.merge_subfolders_button.grid(row=2, column=0, columnspan=2, padx=20, pady=20, sticky="ew")

    def select_source_folder(self):
        source_folder = filedialog.askdirectory(title="Select Source Folder")
        if source_folder:
            self.source_folder_button.configure(text=f"Source Folder: {source_folder}")
            self.source_folder = source_folder

    def select_dest_folder(self):
        dest_folder = filedialog.askdirectory(title="Select Destination Folder")
        if dest_folder:
            self.dest_folder_button.configure(text=f"Destination Folder: {dest_folder}")
            self.dest_folder = dest_folder

    def merge_pdfs(self):
        if hasattr(self, 'source_folder') and hasattr(self, 'dest_folder'):
            source_folder = self.source_folder
            dest_folder = self.dest_folder
            pdf_files = [f for f in os.listdir(source_folder) if f.endswith('.pdf')]
            total_files = len(pdf_files)

            # Define a function to run in a separate thread
            def merge_thread():
                merger = PdfMerger()
                for i, pdf_file in enumerate(pdf_files):
                    file_path = os.path.join(source_folder, pdf_file)
                    merger.append(file_path)
                    self.progress_var.set((i + 1) / total_files * 100)
                    self.update_idletasks()  # Update the GUI to reflect the progress

                output_path = os.path.join(dest_folder, "merged.pdf")
                merger.write(output_path)
                print("PDFs merged successfully.")

                # Use the after method to delay the success message
                self.after(100, self.show_success_message)

            # Create a thread and start it
            thread = threading.Thread(target=merge_thread)
            thread.start()
        else:
            messagebox.showwarning("Error", "Please select both source and destination folders.")

    def show_success_message(self):
        messagebox.showinfo("Success", "PDFs merged successfully.")

    def merge_pdfs_for_subfolders_gui(self):
        if hasattr(self, 'source_folder') and hasattr(self, 'dest_folder'):
            source_folder = self.source_folder
            dest_folder = self.dest_folder
            pdf_files = []
            total_files = 0

            # Count total files in subfolders
            for folder_name in os.listdir(source_folder):
                folder_path = os.path.join(source_folder, folder_name)
                if os.path.isdir(folder_path):
                    pdf_files.extend([f for f in os.listdir(folder_path) if f.endswith('.pdf')])
                    total_files += len(pdf_files)

            merger = PdfMerger()
            current_progress = 0

            # Define a function to run in a separate thread
            def merge_thread():
                # Merge PDFs from subfolders
                for folder_name in os.listdir(source_folder):
                    folder_path = os.path.join(source_folder, folder_name)
                    if os.path.isdir(folder_path):
                        # Create a PdfMerger instance for each subfolder
                        subfolder_merger = PdfMerger()

                        # Get all PDF files in the subfolder
                        pdf_files = [f for f in os.listdir(folder_path) if f.endswith('.pdf')]

                        # Merge each PDF file in the subfolder
                        for pdf_file in pdf_files:
                            file_path = os.path.join(folder_path, pdf_file)
                            subfolder_merger.append(file_path)

                        # Update progress for the current subfolder
                        nonlocal current_progress
                        current_progress += len(pdf_files)
                        self.progress_var.set(current_progress / total_files * 100)
                        self.update_idletasks()  # Update the GUI to reflect the progress

                        # Save the merged PDF for the subfolder
                        output_path = os.path.join(dest_folder, f"{folder_name}_merged.pdf")
                        subfolder_merger.write(output_path)
                        print(f"PDFs in '{folder_name}' merged successfully. Saved as '{output_path}'")

                print("PDFs from subfolders merged successfully.")
                messagebox.showinfo("Success", "PDFs from subfolders merged successfully.")

            # Create a thread and start it
            thread = threading.Thread(target=merge_thread)
            thread.start()
        else:
            messagebox.showwarning("Error", "Please select both source and destination folders.")

if __name__ == "__main__":
    app = PDFMergerApp()
    app.mainloop()

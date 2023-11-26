import tkinter.filedialog
import tkinter.messagebox
from tkinter import *

import customtkinter
from PIL import Image, ImageTk, ImageFilter

from blur_tools import blur


class ResultWindow(customtkinter.CTk):
    __curr_opened_img = None
    __curr_img = None
    __curr_photo_img = None
    __curr_opened_img_file_name = ""

    __padding = 5

    def __init__(self, title, width, height, **kwargs):
        super().__init__(**kwargs)
        super().geometry(f'{width}x{height}')
        super().title(title)

        self.width = width
        self.height = height

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.controlFrame = customtkinter.CTkFrame(master=self)
        self.controlFrame.grid(row=0, column=0, padx=self.__padding, pady=self.__padding, sticky="nsew")
        self.controlFrame.grid_columnconfigure(0, weight=1)

        self.imageFrame = customtkinter.CTkScrollableFrame(master=self)
        self.imageFrame.grid(row=0, column=1, padx=self.__padding, pady=self.__padding, sticky="nsew")
        self.imageFrame.grid_columnconfigure(0, weight=1)
        self.imageFrame.grid_rowconfigure(0, weight=1)

        self.imageCanvas = customtkinter.CTkCanvas(master=self.imageFrame,
                                                   width=self.width - self.controlFrame.winfo_width(),
                                                   height=self.height - 30)
        self.imageCanvas.grid(row=0, column=0, sticky="nsew")

        self.blurController = customtkinter.CTkSlider(master=self.controlFrame,
                                                      command=self.__on_blur_controller_changed, from_=1, to=25)
        self.blurController.grid(row=0, column=0, padx=self.__padding, pady=self.__padding, sticky="nsew")
        self.blurController.set(0)

        self.openImgBtn = customtkinter.CTkButton(master=self.controlFrame, text="Open image",
                                                  command=self.__on_open_img_btn_clicked)
        self.openImgBtn.grid(row=1, column=0, padx=self.__padding, pady=self.__padding, sticky="nsew")

        self.saveImgBtn = customtkinter.CTkButton(master=self.controlFrame, text="Save image",
                                                  command=self.__on_save_img_btn_clicked)

        self.imagePathLbl = customtkinter.CTkLabel(master=self.controlFrame, text="Undefined path")
        self.imagePathLbl.grid(row=3, column=0, padx=self.__padding, pady=self.__padding, sticky="nsew")

        self.renderTimeLbl = customtkinter.CTkLabel(master=self.controlFrame, text="Render time: undefined")
        self.renderTimeLbl.grid(row=4, column=0, padx=self.__padding, pady=self.__padding, sticky="nsew")

        super().mainloop()

    def __on_blur_controller_changed(self, value):
        if self.__curr_opened_img is not None and isinstance(self.__curr_opened_img, Image.Image):
            self.__curr_img = blur.blur(value)
            self.renderTimeLbl.configure(True, text=f"Render time: {blur.render_time} sec.")
            self.__update_image(self.__curr_img)

    def __on_save_img_btn_clicked(self):
        path = self.__curr_opened_img_file_name[:-4] + "_blured" + self.__curr_opened_img_file_name[-4:]
        self.__curr_img.save(path)
        tkinter.messagebox.showinfo("Save info", f"Image saved. Path: {path}")

    def __on_open_img_btn_clicked(self):
        filetypes = (
            ('JPG files', '*.JPG'),
            ('PNG files', '*.PNG')
        )

        filename = tkinter.filedialog.askopenfilename(
            title='Open an image to blur',
            initialdir='./images',
            filetypes=filetypes
        )

        if filename != '':
            self.blurController.set(0)
            self.saveImgBtn.grid(row=2, column=0, padx=self.__padding, pady=self.__padding, sticky="nsew")
            self.imagePathLbl.configure(True, text=filename[:30] + "...")
            self.__curr_opened_img_file_name = filename
            self.__curr_opened_img = Image.open(filename).resize((self.imageCanvas.winfo_width(),
                                                                  self.imageCanvas.winfo_height()))
            self.__update_image(self.__curr_opened_img)
            blur.set_image(self.__curr_opened_img)

    def __update_image(self, image):
        if self.__curr_opened_img is not None and isinstance(image, Image.Image):
            self.__curr_img = image
            self.__curr_photo_img = ImageTk.PhotoImage(image)
            self.imageCanvas.config(height=image.height, width=image.width)
            self.imageCanvas.create_image(0, 0, anchor=NW, image=self.__curr_photo_img)

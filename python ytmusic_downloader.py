import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import subprocess
import threading
import os

class YTMusicDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("YT Music Downloader")
        self.root.geometry("820x780")
        self.root.configure(bg="#0d0d0d")
        self.root.resizable(False, False)

        self.download_dir = tk.StringVar()
        self.url = tk.StringVar()
        self.channel_url = tk.StringVar()
        self.use_cookies = tk.BooleanVar(value=False)
        self.browser = tk.StringVar(value="chrome")
        self.mode = tk.StringVar(value="video")  # "video", "playlist", or "channel"
        self.scanned_urls = []

        self.build_ui()

    def build_ui(self):
        # Title
        tk.Label(
            self.root,
            text="🎵 YT MUSIC DOWNLOADER",
            font=("Segoe UI", 16, "bold"),
            fg="#ff1a1a", bg="#0d0d0d"
        ).pack(pady=(15, 2))

        tk.Label(
            self.root,
            text="Download single videos, playlists, or your entire channel",
            font=("Segoe UI", 10),
            fg="#888888", bg="#0d0d0d"
        ).pack(pady=(0, 12))

        # Mode selector
        mode_frame = tk.Frame(self.root, bg="#0d0d0d")
        mode_frame.pack(fill="x", padx=30, pady=(0, 10))

        tk.Label(
            mode_frame, text="Mode:",
            font=("Segoe UI", 10, "bold"),
            fg="#ff1a1a", bg="#0d0d0d"
        ).pack(side="left", padx=(0, 10))

        for value, label in [
            ("video", "Single Video"),
            ("playlist", "Full Playlist"),
            ("channel", "Scan My Channel"),
        ]:
            tk.Radiobutton(
                mode_frame, text=label,
                variable=self.mode, value=value,
                font=("Segoe UI", 10),
                fg="#cccccc", bg="#0d0d0d",
                selectcolor="#1a1a1a",
                activebackground="#0d0d0d", activeforeground="#ff1a1a",
                cursor="hand2",
                command=self.update_mode
            ).pack(side="left", padx=5)

        # URL input
        url_frame = tk.Frame(self.root, bg="#0d0d0d")
        url_frame.pack(fill="x", padx=30, pady=5)

        self.url_label = tk.Label(
            url_frame, text="Video URL:",
            font=("Segoe UI", 10, "bold"),
            fg="#ff1a1a", bg="#0d0d0d"
        )
        self.url_label.pack(anchor="w")

        url_entry = tk.Entry(
            url_frame, textvariable=self.url,
            font=("Segoe UI", 10),
            bg="#1a1a1a", fg="#ffffff",
            insertbackground="#ff1a1a",
            relief="flat", bd=8
        )
        url_entry.pack(fill="x", pady=(5, 0), ipady=5)

        # Channel URL (only visible in channel mode)
        self.channel_frame = tk.Frame(self.root, bg="#0d0d0d")

        tk.Label(
            self.channel_frame, text="Channel URL:",
            font=("Segoe UI", 10, "bold"),
            fg="#ff1a1a", bg="#0d0d0d"
        ).pack(anchor="w")

        channel_row = tk.Frame(self.channel_frame, bg="#0d0d0d")
        channel_row.pack(fill="x", pady=(5, 0))

        tk.Entry(
            channel_row, textvariable=self.channel_url,
            font=("Segoe UI", 10),
            bg="#1a1a1a", fg="#ffffff",
            insertbackground="#ff1a1a",
            relief="flat", bd=8
        ).pack(side="left", fill="x", expand=True, ipady=5)

        self.scan_btn = tk.Button(
            channel_row, text="🔍 SCAN",
            command=self.start_scan,
            font=("Segoe UI", 9, "bold"),
            bg="#ff1a1a", fg="#ffffff",
            activebackground="#cc0000", activeforeground="#ffffff",
            relief="flat", bd=0, padx=15, pady=6, cursor="hand2"
        )
        self.scan_btn.pack(side="left", padx=(10, 0))

        # Save folder
        dir_frame = tk.Frame(self.root, bg="#0d0d0d")
        dir_frame.pack(fill="x", padx=30, pady=12)

        tk.Label(
            dir_frame, text="Save To:",
            font=("Segoe UI", 10, "bold"),
            fg="#ff1a1a", bg="#0d0d0d"
        ).pack(anchor="w")

        dir_row = tk.Frame(dir_frame, bg="#0d0d0d")
        dir_row.pack(fill="x", pady=(5, 0))

        tk.Entry(
            dir_row, textvariable=self.download_dir,
            font=("Segoe UI", 10),
            bg="#1a1a1a", fg="#ffffff",
            insertbackground="#ff1a1a",
            relief="flat", bd=8
        ).pack(side="left", fill="x", expand=True, ipady=5)

        tk.Button(
            dir_row, text="BROWSE",
            command=self.pick_directory,
            font=("Segoe UI", 9, "bold"),
            bg="#ff1a1a", fg="#ffffff",
            activebackground="#cc0000", activeforeground="#ffffff",
            relief="flat", bd=0, padx=15, pady=6, cursor="hand2"
        ).pack(side="left", padx=(10, 0))

        # Cookies
        cookie_frame = tk.Frame(self.root, bg="#0d0d0d")
        cookie_frame.pack(fill="x", padx=30, pady=(0, 8))

        tk.Checkbutton(
            cookie_frame,
            text="Use browser cookies (for private/unlisted content)",
            variable=self.use_cookies,
            font=("Segoe UI", 9),
            fg="#cccccc", bg="#0d0d0d",
            selectcolor="#1a1a1a",
            activebackground="#0d0d0d", activeforeground="#ff1a1a",
            cursor="hand2"
        ).pack(anchor="w")

        browser_row = tk.Frame(cookie_frame, bg="#0d0d0d")
        browser_row.pack(anchor="w", pady=(5, 0))

        tk.Label(
            browser_row, text="Browser:",
            font=("Segoe UI", 9),
            fg="#888888", bg="#0d0d0d"
        ).pack(side="left")

        for b in ["chrome", "firefox", "edge", "brave"]:
            tk.Radiobutton(
                browser_row, text=b.capitalize(),
                variable=self.browser, value=b,
                font=("Segoe UI", 9),
                fg="#cccccc", bg="#0d0d0d",
                selectcolor="#1a1a1a",
                activebackground="#0d0d0d", activeforeground="#ff1a1a",
                cursor="hand2"
            ).pack(side="left", padx=5)

        # Download button
        self.download_btn = tk.Button(
            self.root, text="⬇  DOWNLOAD",
            command=self.start_download,
            font=("Segoe UI", 12, "bold"),
            bg="#ff1a1a", fg="#ffffff",
            activebackground="#cc0000", activeforeground="#ffffff",
            relief="flat", bd=0, pady=12, cursor="hand2"
        )
        self.download_btn.pack(fill="x", padx=30, pady=(10, 12))

        # Log
        tk.Label(
            self.root, text="Progress:",
            font=("Segoe UI", 10, "bold"),
            fg="#ff1a1a", bg="#0d0d0d"
        ).pack(anchor="w", padx=30)

        self.log = scrolledtext.ScrolledText(
            self.root,
            bg="#000000", fg="#ff1a1a",
            insertbackground="#ff1a1a",
            font=("Consolas", 9),
            relief="flat", bd=8, height=13,
            wrap="word"
        )
        self.log.pack(fill="both", expand=True, padx=30, pady=(5, 15))

    def update_mode(self):
        mode = self.mode.get()

        # Show/hide channel frame
        if mode == "channel":
            self.channel_frame.pack(fill="x", padx=30, pady=8, before=self.download_btn.master.children.get('!frame') or None)
        else:
            self.channel_frame.pack_forget()

        # Update labels
        if mode == "video":
            self.url_label.config(text="Video URL:")
            self.download_btn.config(text="⬇  DOWNLOAD VIDEO")
        elif mode == "playlist":
            self.url_label.config(text="Playlist URL:")
            self.download_btn.config(text="⬇  DOWNLOAD PLAYLIST")
        else:
            self.url_label.config(text="(or paste a specific video/playlist URL above — optional)")
            self.download_btn.config(text="⬇  DOWNLOAD ALL SCANNED")

    def pick_directory(self):
        folder = filedialog.askdirectory(title="Select download folder")
        if folder:
            self.download_dir.set(folder)

    def log_message(self, msg):
        self.log.insert(tk.END, msg + "\n")
        self.log.see(tk.END)
        self.root.update_idletasks()

    def _build_common_flags(self):
        flags = [
            "-x",
            "--audio-format", "mp3",
            "--embed-thumbnail",
            "--embed-metadata",
            "--no-overwrites",
            "--ignore-errors",
        ]
        if self.use_cookies.get():
            flags += ["--cookies-from-browser", self.browser.get()]
        return flags

    # ---------- SCAN ----------
    def start_scan(self):
        channel = self.channel_url.get().strip()
        if not channel:
            messagebox.showerror("Missing URL", "Please paste your channel URL.")
            return

        self.scan_btn.config(state="disabled", text="⏳ SCANNING...")
        self.log.delete("1.0", tk.END)
        self.log_message(f"Scanning channel: {channel}\nThis may take a moment...\n")

        threading.Thread(target=self.run_scan, args=(channel,), daemon=True).start()

    def run_scan(self, channel):
        try:
            cmd = [
                "yt-dlp",
                "--flat-playlist",
                "--print", "%(url)s",
                "--no-warnings",
            ]
            if self.use_cookies.get():
                cmd += ["--cookies-from-browser", self.browser.get()]
            cmd.append(channel)

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
            )

            stdout, stderr = process.communicate()
            urls = [line.strip() for line in stdout.splitlines() if line.strip().startswith("http")]

            self.scanned_urls = urls

            if urls:
                self.log_message(f"✅ Found {len(urls)} videos:\n")
                for i, u in enumerate(urls, 1):
                    self.log_message(f"  {i}. {u}")
                self.root.after(0, lambda: messagebox.showinfo(
                    "Scan Complete",
                    f"Found {len(urls)} videos.\nClick DOWNLOAD ALL SCANNED to grab them."
                ))
            else:
                self.log_message("⚠ No videos found. Check the channel URL.")
                if stderr:
                    self.log_message("\nDetails:\n" + stderr[:800])
                self.root.after(0, lambda: messagebox.showwarning(
                    "No videos found", "No videos were detected. Check the URL."
                ))

        except FileNotFoundError:
            self.log_message("❌ yt-dlp not found. Install with: winget install yt-dlp")
            self.root.after(0, lambda: messagebox.showerror(
                "yt-dlp not found", "yt-dlp is not installed or not in PATH."
            ))
        except Exception as e:
            self.log_message(f"❌ ERROR: {e}")
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        finally:
            self.root.after(0, lambda: self.scan_btn.config(state="normal", text="🔍 SCAN"))

    # ---------- DOWNLOAD ----------
    def start_download(self):
        mode = self.mode.get()
        out_dir = self.download_dir.get().strip()

        if not out_dir:
            messagebox.showerror("Missing Folder", "Please pick a download folder.")
            return
        if not os.path.isdir(out_dir):
            messagebox.showerror("Invalid Folder", "The selected folder does not exist.")
            return

        # Channel mode requires a scan first
        if mode == "channel":
            if not self.scanned_urls:
                messagebox.showerror("No Scan Yet", "Click 🔍 SCAN first to find your videos.")
                return
            self.download_btn.config(state="disabled", text="⏳  DOWNLOADING...")
            self.log_message(f"\nStarting batch download of {len(self.scanned_urls)} videos...\n")
            threading.Thread(target=self.run_batch_download,
                             args=(self.scanned_urls, out_dir), daemon=True).start()
            return

        # Video / playlist mode
        url = self.url.get().strip()
        if not url:
            messagebox.showerror("Missing URL", "Please paste a URL.")
            return

        self.download_btn.config(state="disabled", text="⏳  DOWNLOADING...")
        self.log.delete("1.0", tk.END)
        self.log_message(f"Starting download...\nMode: {mode}\nURL: {url}\nFolder: {out_dir}\n")

        threading.Thread(target=self.run_single_download,
                         args=(url, out_dir, mode), daemon=True).start()

    def run_single_download(self, url, out_dir, mode):
        try:
            if mode == "playlist":
                template = os.path.join(out_dir, "%(playlist)s", "%(title)s.%(ext)s")
            else:
                template = os.path.join(out_dir, "%(title)s.%(ext)s")

            cmd = ["yt-dlp"] + self._build_common_flags() + ["-o", template]

            if mode == "video":
                cmd.append("--no-playlist")

            cmd.append(url)
            self._execute(cmd)

        except Exception as e:
            self.log_message(f"❌ ERROR: {e}")
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        finally:
            self.root.after(0, self._reset_button)

    def run_batch_download(self, urls, out_dir):
        try:
            # Write URLs to a temporary file so yt-dlp can read them all at once
            batch_file = os.path.join(out_dir, "_scan_batch.txt")
            with open(batch_file, "w", encoding="utf-8") as f:
                f.write("\n".join(urls))

            template = os.path.join(out_dir, "%(title)s.%(ext)s")
            cmd = ["yt-dlp"] + self._build_common_flags() + [
                "-o", template,
                "--batch-file", batch_file,
            ]

            self.log_message("Command:\n" + " ".join(f'"{c}"' if " " in c else c for c in cmd) + "\n")
            self.log_message("-" * 60)

            self._execute(cmd, already_printed=True)

            # Clean up the temp file
            try:
                os.remove(batch_file)
            except OSError:
                pass

        except Exception as e:
            self.log_message(f"❌ ERROR: {e}")
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        finally:
            self.root.after(0, self._reset_button)

    def _execute(self, cmd, already_printed=False):
        if not already_printed:
            self.log_message("Command:\n" + " ".join(f'"{c}"' if " " in c else c for c in cmd) + "\n")
            self.log_message("-" * 60)

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
        )

        for line in process.stdout:
            self.log_message(line.rstrip())

        process.wait()

        if process.returncode == 0:
            self.log_message("\n" + "=" * 60)
            self.log_message("✅ DONE!")
            self.root.after(0, lambda: messagebox.showinfo("Success", "Download complete!"))
        else:
            self.log_message("\n" + "=" * 60)
            self.log_message(f"⚠ Finished with exit code {process.returncode}.")
            self.root.after(0, lambda: messagebox.showwarning(
                "Completed with warnings",
                "Finished, but some items may have failed. Check the log."
            ))

    def _reset_button(self):
        mode = self.mode.get()
        if mode == "video":
            self.download_btn.config(state="normal", text="⬇  DOWNLOAD VIDEO")
        elif mode == "playlist":
            self.download_btn.config(state="normal", text="⬇  DOWNLOAD PLAYLIST")
        else:
            self.download_btn.config(state="normal", text="⬇  DOWNLOAD ALL SCANNED")


if __name__ == "__main__":
    root = tk.Tk()
    app = YTMusicDownloader(root)
    root.mainloop()
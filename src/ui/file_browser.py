import os
import tkinter as tk
from tkinter import ttk, filedialog

class FileBrowser(ttk.Frame):
    def __init__(self, parent, initial_dir=None, on_file_select=None):
        super().__init__(parent)
        self.parent = parent
        self.initial_dir = initial_dir
        self.on_file_select = on_file_select
        self.data_folder = None
        
        self.setup_ui()
        
        if initial_dir and os.path.exists(initial_dir):
            self.data_folder = initial_dir
            self.refresh_files()

    def setup_ui(self):
        """Setup the file browser UI components."""
        # Create main frame
        self.files_frame = ttk.LabelFrame(self, text="Data Files")
        self.files_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create buttons frame
        buttons_frame = ttk.Frame(self.files_frame)
        buttons_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Button(buttons_frame, text="Open Data Folder", 
                  command=self.load_data_folder).pack(side=tk.LEFT, padx=2)
        ttk.Button(buttons_frame, text="Refresh Files",
                  command=self.refresh_files).pack(side=tk.LEFT, padx=2)
        
        # Create tree frame with scrollbars
        tree_frame = ttk.Frame(self.files_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Create and configure the Treeview
        self.file_tree = ttk.Treeview(
            tree_frame,
            selectmode='browse',
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set,
            height=15
        )
        self.file_tree.pack(fill=tk.BOTH, expand=True)
        
        # Configure scrollbars
        vsb.config(command=self.file_tree.yview)
        hsb.config(command=self.file_tree.xview)
        
        # Configure tree columns and heading
        self.file_tree.heading('#0', text='Name', anchor=tk.W)
        
        # Configure tags for icons
        self.file_tree.tag_configure('folder', foreground='lightblue')
        self.file_tree.tag_configure('file', foreground='white')
        
        # Bind events
        self.file_tree.bind('<<TreeviewSelect>>', self._on_file_select)
        self.file_tree.bind('<Double-1>', self._on_tree_double_click)

    def load_data_folder(self):
        """Open a folder dialog and load all CSV files from the selected directory."""
        folder = filedialog.askdirectory(
            title="Select Data Folder",
            initialdir=self.initial_dir,
            mustexist=True
        )
        if folder:
            self.data_folder = folder
            self.refresh_files()
            
            # Automatically expand all folders
            def expand_all(tree, item=""):
                children = tree.get_children(item)
                for child in children:
                    tree.item(child, open=True)
                    expand_all(tree, child)
            
            expand_all(self.file_tree)

    def refresh_files(self):
        """Refresh the file tree with all CSV files in the data folder."""
        if not self.data_folder:
            return
            
        # Clear existing items
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
            
        # Collect all CSV files and their paths
        all_files = []
        for root, _, files in os.walk(self.data_folder):
            for file in files:
                if file.upper().endswith('.CSV'):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(root, self.data_folder)
                    all_files.append((rel_path, file, full_path))
        
        # Sort files to get folders at top
        def sort_key(item):
            rel_path, file, _ = item
            # Use a tuple for sorting: (is_root, path_parts, filename)
            path_parts = rel_path.split(os.sep)
            return (rel_path == '.', len(path_parts), path_parts, file.upper())
            
        all_files.sort(key=sort_key)
        
        # Dictionary to keep track of folder nodes
        folders = {}
        
        # Process all files
        for rel_path, file, full_path in all_files:
            if rel_path == '.':
                # Root level files - add at bottom
                continue
            else:
                # Create folder hierarchy if needed
                parts = rel_path.split(os.sep)
                current = ""
                
                # Create parent folders if they don't exist
                for part in parts:
                    parent = current
                    current = os.path.join(current, part) if current else part
                    
                    if current not in folders:
                        folders[current] = self.file_tree.insert(
                            "",
                            'end',
                            text=part,
                            values=(os.path.join(self.data_folder, current),),
                            tags=('folder',),
                            open=True
                        )
                
                # Add file under its folder
                self.file_tree.insert(
                    folders[rel_path],
                    'end',
                    text=file,
                    values=(full_path,),
                    tags=('file',)
                )
        
        # Finally add root level files at the bottom
        for rel_path, file, full_path in all_files:
            if rel_path == '.':
                self.file_tree.insert(
                    "",
                    'end',
                    text=file,
                    values=(full_path,),
                    tags=('file',)
                )

    def _on_file_select(self, event):
        """Handle file selection from tree."""
        selection = self.file_tree.selection()
        if not selection:
            return
            
        item = selection[0]
        item_tags = self.file_tree.item(item)['tags']
        
        # Skip if a folder is selected
        if 'folder' in item_tags:
            return
            
        # Get the full file path from the tree item values
        file_path = self.file_tree.item(item)['values'][0]
        if not os.path.isfile(file_path):
            return
            
        if self.on_file_select:
            self.on_file_select(file_path)

    def _on_tree_double_click(self, event):
        """Handle double click on tree items."""
        item = self.file_tree.selection()
        if not item:
            return
            
        item = item[0]
        if 'folder' in self.file_tree.item(item, 'tags'):
            # Toggle folder expansion
            if self.file_tree.item(item, 'open'):
                self.file_tree.item(item, open=False)
            else:
                self.file_tree.item(item, open=True)

    def setup_file_tree(self):
        """Setup the file tree widget."""
        self.file_tree = ttk.Treeview(self, selectmode='browse', show='tree')
        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure tags
        theme = self.master.master.master.theme_manager.get_current_theme()
        if theme:
            self.file_tree.tag_configure('file', foreground=theme['ui']['fg'])
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.file_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_tree.configure(yscrollcommand=scrollbar.set) 
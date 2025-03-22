import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import matplotlib.pyplot as plt
import networkx as nx
import requests
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class SkincareCompanion:
    def __init__(self):
        # ------- DATA STRUCTURES -------
        
        # Skincare ingredient compatibility database
        self.ingredient_interactions = {
            "retinol": {
                "conflicts": ["glycolic acid", "salicylic acid", "vitamin c", "benzoyl peroxide"],
                "waiting_time": 30,  # minutes
                "frequency": "once daily",
                "climate_adjustments": {
                    "high_humidity": "reduce concentration",
                    "low_humidity": "add moisturizer after",
                    "high_uv": "night only",
                    "high_pollution": "follow with antioxidants"
                }
            },
            "vitamin c": {
                "conflicts": ["retinol", "glycolic acid", "niacinamide"],
                "waiting_time": 15,
                "frequency": "once daily",
                "climate_adjustments": {
                    "high_humidity": "lighter formulation",
                    "low_humidity": "standard application",
                    "high_uv": "morning application",
                    "high_pollution": "increase frequency"
                }
            },
            "niacinamide": {
                "conflicts": ["vitamin c"],
                "waiting_time": 10,
                "frequency": "twice daily",
                "climate_adjustments": {
                    "high_humidity": "standard application",
                    "low_humidity": "use with hyaluronic acid",
                    "high_uv": "combine with sunscreen",
                    "high_pollution": "standard application"
                }
            },
            "hyaluronic acid": {
                "conflicts": [],
                "waiting_time": 1,
                "frequency": "twice daily",
                "climate_adjustments": {
                    "high_humidity": "standard application",
                    "low_humidity": "apply to damp skin",
                    "high_uv": "standard application",
                    "high_pollution": "standard application"
                }
            },
            "glycolic acid": {
                "conflicts": ["retinol", "vitamin c", "salicylic acid"],
                "waiting_time": 20,
                "frequency": "2-3 times weekly",
                "climate_adjustments": {
                    "high_humidity": "standard application",
                    "low_humidity": "reduce frequency",
                    "high_uv": "night only",
                    "high_pollution": "standard application"
                }
            },
            "salicylic acid": {
                "conflicts": ["retinol", "glycolic acid"],
                "waiting_time": 20,
                "frequency": "2-3 times weekly",
                "climate_adjustments": {
                    "high_humidity": "standard application",
                    "low_humidity": "reduce frequency",
                    "high_uv": "night only",
                    "high_pollution": "standard application"
                }
            },
            "benzoyl peroxide": {
                "conflicts": ["retinol", "vitamin c"],
                "waiting_time": 20,
                "frequency": "once daily",
                "climate_adjustments": {
                    "high_humidity": "standard application",
                    "low_humidity": "follow with moisturizer",
                    "high_uv": "night only",
                    "high_pollution": "standard application"
                }
            },
            "azelaic acid": {
                "conflicts": [],
                "waiting_time": 10,
                "frequency": "twice daily",
                "climate_adjustments": {
                    "high_humidity": "standard application",
                    "low_humidity": "standard application",
                    "high_uv": "standard application",
                    "high_pollution": "standard application"
                }
            },
            "peptides": {
                "conflicts": ["acids"],
                "waiting_time": 10,
                "frequency": "twice daily",
                "climate_adjustments": {
                    "high_humidity": "standard application",
                    "low_humidity": "standard application",
                    "high_uv": "standard application",
                    "high_pollution": "standard application"
                }
            }
        }
        
        # Sample climate data influences on skincare
        self.climate_effects = {
            "high_humidity": {
                "recommended": ["lightweight moisturizer", "oil-free", "mattifying"],
                "avoid": ["heavy oils", "thick creams", "oil-based products"],
                "increase": ["exfoliation"],
                "decrease": ["heavy hydration"]
            },
            "low_humidity": {
                "recommended": ["rich moisturizer", "facial oils", "hydrating masks"],
                "avoid": ["harsh cleansers", "alcohol-based products"],
                "increase": ["hydration layers"],
                "decrease": ["exfoliation frequency"]
            },
            "high_uv": {
                "recommended": ["sunscreen", "antioxidants", "vitamin C"],
                "avoid": ["photosensitizing ingredients during day"],
                "increase": ["sun protection"],
                "decrease": ["exfoliation"]
            },
            "high_pollution": {
                "recommended": ["double cleansing", "antioxidants", "barrier repair"],
                "avoid": ["skip cleansing"],
                "increase": ["antioxidant protection"],
                "decrease": []
            }
        }
        
        # Common skincare ingredients for autocomplete
        self.common_ingredients = list(self.ingredient_interactions.keys()) + [
            "ceramides", "squalane", "glycerin", "panthenol", "centella asiatica",
            "green tea extract", "aloe vera", "allantoin", "urea", "lactic acid",
            "mandelic acid", "zinc oxide", "titanium dioxide", "bakuchiol", "coenzyme q10"
        ]
        
        # Sample products for demo
        self.sample_products = [
            {
                "name": "Gentle Cleanser",
                "ingredients": ["glycerin", "panthenol"],
                "preferred_time": "both"
            },
            {
                "name": "Vitamin C Serum",
                "ingredients": ["vitamin c", "ferulic acid"],
                "preferred_time": "morning"
            },
            {
                "name": "Retinol Night Cream",
                "ingredients": ["retinol", "ceramides"],
                "preferred_time": "evening"
            },
            {
                "name": "Hyaluronic Acid Serum",
                "ingredients": ["hyaluronic acid", "glycerin"],
                "preferred_time": "both"
            },
            {
                "name": "AHA Exfoliant",
                "ingredients": ["glycolic acid", "lactic acid"],
                "preferred_time": "evening"
            }
        ]

    def analyze_skincare_routine(self, products):
        """Analyze skincare routine for conflicts and create an interaction map"""
        all_ingredients = set()
        for product in products:
            all_ingredients.update(product["ingredients"])
        
        # Identify conflicts
        conflicts = []
        for product1 in products:
            for ingredient1 in product1["ingredients"]:
                if ingredient1 in self.ingredient_interactions:
                    conflict_list = self.ingredient_interactions[ingredient1].get("conflicts", [])
                    for product2 in products:
                        if product1 != product2:  # Don't compare the same product
                            for ingredient2 in product2["ingredients"]:
                                if ingredient2 in conflict_list:
                                    conflicts.append({
                                        "product1": product1["name"],
                                        "ingredient1": ingredient1,
                                        "product2": product2["name"],
                                        "ingredient2": ingredient2,
                                        "waiting_time": self.ingredient_interactions[ingredient1].get("waiting_time", 0)
                                    })
        
        # Create a graph for visualization
        G = nx.Graph()
        
        # Add products as nodes
        for product in products:
            G.add_node(product["name"], type="product")
            
            # Add ingredient nodes and connect to products
            for ingredient in product["ingredients"]:
                if ingredient not in G:
                    G.add_node(ingredient, type="ingredient")
                G.add_edge(product["name"], ingredient, type="contains")
        
        # Add conflict edges
        for conflict in conflicts:
            if conflict["ingredient1"] in G and conflict["ingredient2"] in G:
                G.add_edge(conflict["ingredient1"], conflict["ingredient2"], type="conflict", 
                           waiting_time=conflict["waiting_time"])
        
        return {
            "conflicts": conflicts,
            "graph": G
        }

    def create_application_schedule(self, products, days=7):
        """Create an optimized weekly application schedule for skincare products"""
        schedule = {i: {"morning": [], "evening": []} for i in range(1, days+1)}
        
        # Map products to appropriate slots based on frequency and conflicts
        for product in products:
            active_ingredients = [i for i in product["ingredients"] 
                                if i in self.ingredient_interactions]
            
            if not active_ingredients:
                # Products without active ingredients can be used daily
                for day in range(1, days+1):
                    if product["preferred_time"] in ["morning", "both"]:
                        schedule[day]["morning"].append(product["name"])
                    if product["preferred_time"] in ["evening", "both"]:
                        schedule[day]["evening"].append(product["name"])
            else:
                # Products with active ingredients need strategic scheduling
                primary_active = active_ingredients[0]
                freq = self.ingredient_interactions[primary_active]["frequency"]
                
                if freq == "twice daily":
                    for day in range(1, days+1):
                        schedule[day]["morning"].append(product["name"])
                        schedule[day]["evening"].append(product["name"])
                elif freq == "once daily":
                    for day in range(1, days+1):
                        time_slot = "evening" if primary_active in ["retinol", "glycolic acid"] else "morning"
                        schedule[day][time_slot].append(product["name"])
                elif "weekly" in freq:
                    # Extract number from string like "2-3 times weekly"
                    times = int(freq.split()[0].split("-")[0])
                    interval = max(1, days // times)
                    for day in range(1, days+1, interval):
                        time_slot = "evening" if primary_active in ["retinol", "glycolic acid"] else "morning"
                        schedule[day][time_slot].append(product["name"])
        
        return schedule

    def adjust_for_climate(self, routine, home_climate, destination_climate):
        """Adjust skincare routine based on climate differences"""
        adjustments = []
        
        # Determine climate changes
        climate_changes = []
        if destination_climate["humidity"] - home_climate["humidity"] > 20:
            climate_changes.append("high_humidity")
        elif home_climate["humidity"] - destination_climate["humidity"] > 20:
            climate_changes.append("low_humidity")
            
        if destination_climate["uv_index"] - home_climate["uv_index"] > 2:
            climate_changes.append("high_uv")
            
        if destination_climate["pollution_index"] - home_climate["pollution_index"] > 20:
            climate_changes.append("high_pollution")
        
        # Make routine adjustments based on climate changes
        adjusted_routine = []
        for product in routine:
            active_ingredients = [i for i in product["ingredients"] 
                                if i in self.ingredient_interactions]
            
            product_adjustments = []
            for ingredient in active_ingredients:
                for climate_change in climate_changes:
                    if ingredient in self.ingredient_interactions:
                        adjustment = self.ingredient_interactions[ingredient]["climate_adjustments"].get(climate_change)
                        if adjustment:
                            product_adjustments.append({
                                "product": product["name"],
                                "ingredient": ingredient,
                                "climate_factor": climate_change,
                                "adjustment": adjustment
                            })
            
            if product_adjustments:
                for adj in product_adjustments:
                    adjustments.append(adj)
            
            # Include product in adjusted routine
            adjusted_routine.append(product)
        
        # Add climate-specific recommendations
        for climate_change in climate_changes:
            if climate_change in self.climate_effects:
                for category, items in self.climate_effects[climate_change].items():
                    if category in ["recommended", "avoid"]:
                        for item in items:
                            adjustments.append({
                                "product": None,
                                "ingredient": None,
                                "climate_factor": climate_change,
                                "adjustment_type": category,
                                "adjustment": item
                            })
        
        return {
            "climate_changes": climate_changes,
            "adjusted_routine": adjusted_routine,
            "adjustments": adjustments
        }

    def get_climate_data(self, location):
        """
        Get climate data for a location (simulated)
        In a real app, this would connect to a weather/climate API
        """
        # Sample climate data for demonstration
        climate_data = {
            "New York": {
                "humidity": 60,
                "uv_index": 5,
                "pollution_index": 40
            },
            "Los Angeles": {
                "humidity": 50,
                "uv_index": 8,
                "pollution_index": 60
            },
            "Miami": {
                "humidity": 80,
                "uv_index": 9,
                "pollution_index": 30
            },
            "Denver": {
                "humidity": 25,
                "uv_index": 7,
                "pollution_index": 20
            },
            "Seattle": {
                "humidity": 70,
                "uv_index": 4,
                "pollution_index": 25
            },
            "Phoenix": {
                "humidity": 20,
                "uv_index": 10,
                "pollution_index": 45
            },
            "Chicago": {
                "humidity": 55,
                "uv_index": 5,
                "pollution_index": 50
            },
            "Honolulu": {
                "humidity": 75,
                "uv_index": 10,
                "pollution_index": 15
            },
            "Tokyo": {
                "humidity": 65,
                "uv_index": 6,
                "pollution_index": 70
            },
            "London": {
                "humidity": 75,
                "uv_index": 3,
                "pollution_index": 45
            },
            "Dubai": {
                "humidity": 60,
                "uv_index": 11,
                "pollution_index": 65
            },
            "Sydney": {
                "humidity": 60,
                "uv_index": 9,
                "pollution_index": 25
            }
        }
        
        # Default values if location not found
        default_data = {
            "humidity": 50,
            "uv_index": 5,
            "pollution_index": 40
        }
        
        return climate_data.get(location, default_data)

    def visualize_conflicts(self, analysis_result):
        """Generate a visual representation of product/ingredient conflicts"""
        G = analysis_result["graph"]
        
        # Create figure
        plt.figure(figsize=(12, 8))
        
        # Define node colors based on type
        node_colors = []
        for node in G.nodes():
            if G.nodes[node].get("type") == "product":
                node_colors.append("skyblue")
            else:
                node_colors.append("lightgreen")
        
        # Define edge colors based on type
        edge_colors = []
        for u, v, data in G.edges(data=True):
            if data.get("type") == "conflict":
                edge_colors.append("red")
            else:
                edge_colors.append("gray")
        
        # Create layout
        pos = nx.spring_layout(G, seed=42)
        
        # Draw nodes
        nx.draw_networkx_nodes(G, pos, node_size=700, node_color=node_colors, alpha=0.8)
        
        # Draw edges
        nx.draw_networkx_edges(G, pos, edge_color=edge_colors, width=2, alpha=0.7)
        
        # Draw labels
        nx.draw_networkx_labels(G, pos, font_size=10, font_family="sans-serif")
        
        plt.axis("off")
        plt.tight_layout()
        
        return plt.gcf()

    def visualize_schedule(self, schedule):
        """Generate a visual representation of the weekly skincare schedule"""
        days = list(schedule.keys())
        
        # Count max products per time slot
        max_products_morning = max(len(schedule[day]["morning"]) for day in days)
        max_products_evening = max(len(schedule[day]["evening"]) for day in days)
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Set up the table
        cell_text = []
        for day in days:
            morning_products = ', '.join(schedule[day]["morning"])
            evening_products = ', '.join(schedule[day]["evening"])
            cell_text.append([f"Day {day}", morning_products, evening_products])
        
        # Create table
        table = ax.table(
            cellText=cell_text,
            colLabels=["Day", "Morning Routine", "Evening Routine"],
            loc="center",
            cellLoc="center"
        )
        
        # Modify table appearance
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 1.5)
        
        # Hide axes
        ax.axis("off")
        ax.set_title("Weekly Skincare Schedule")
        
        return fig


class SkincareAppGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Skincare Routine Analyzer & Climate Adjuster")
        self.root.geometry("900x700")
        
        self.skincare_companion = SkincareCompanion()
        
        # Initialize variables
        self.products = self.skincare_companion.sample_products.copy()  # Moved here
        
        # Create notebook with tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_product_tab()  # Now self.products is defined
        self.create_analysis_tab()
        self.create_schedule_tab()
        self.create_climate_tab()
        
        # Initialize variables
        self.products = self.skincare_companion.sample_products.copy()
        
    def create_product_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Products")
        
        # Products frame
        products_frame = ttk.LabelFrame(tab, text="Your Skincare Products")
        products_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Product list
        self.product_listbox = tk.Listbox(products_frame, height=10, width=40)
        self.product_listbox.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar = ttk.Scrollbar(products_frame, orient="vertical", command=self.product_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.product_listbox.config(yscrollcommand=scrollbar.set)
        
        # Update product list
        self.update_product_list()
        
        # Product details frame
        details_frame = ttk.LabelFrame(tab, text="Product Details")
        details_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Product name
        ttk.Label(details_frame, text="Product Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.product_name_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.product_name_var, width=40).grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        # Ingredients
        ttk.Label(details_frame, text="Ingredients (comma-separated):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.ingredients_var = tk.StringVar()
        self.ingredients_entry = ttk.Entry(details_frame, textvariable=self.ingredients_var, width=40)
        self.ingredients_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        
        # Preferred time
        ttk.Label(details_frame, text="Preferred Application Time:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.preferred_time_var = tk.StringVar(value="both")
        time_frame = ttk.Frame(details_frame)
        time_frame.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        ttk.Radiobutton(time_frame, text="Morning", variable=self.preferred_time_var, value="morning").pack(side="left", padx=5)
        ttk.Radiobutton(time_frame, text="Evening", variable=self.preferred_time_var, value="evening").pack(side="left", padx=5)
        ttk.Radiobutton(time_frame, text="Both", variable=self.preferred_time_var, value="both").pack(side="left", padx=5)
        
        # Buttons
        button_frame = ttk.Frame(details_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        ttk.Button(button_frame, text="Add Product", command=self.add_product).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Update Selected", command=self.update_product).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Remove Selected", command=self.remove_product).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Clear All", command=self.clear_products).pack(side="left", padx=5)
        
        # Load product details when selected
        self.product_listbox.bind("<<ListboxSelect>>", self.load_product_details)
        
    def create_analysis_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Conflict Analysis")
        
        # Button to analyze
        ttk.Button(tab, text="Analyze Routine for Conflicts", command=self.analyze_routine).pack(pady=10)
        
        # Results area
        results_frame = ttk.LabelFrame(tab, text="Analysis Results")
        results_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Conflicts list
        ttk.Label(results_frame, text="Conflicts:").pack(anchor="w", padx=5, pady=5)
        self.conflicts_text = scrolledtext.ScrolledText(results_frame, height=8, width=80, wrap=tk.WORD)
        self.conflicts_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Graph canvas
        self.graph_frame = ttk.LabelFrame(tab, text="Ingredient Interaction Map")
        self.graph_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    def create_schedule_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Weekly Schedule")
        
        # Button to generate schedule
        ttk.Button(tab, text="Generate Weekly Schedule", command=self.generate_schedule).pack(pady=10)
        
        # Schedule display area
        self.schedule_frame = ttk.Frame(tab)
        self.schedule_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    def create_climate_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Travel Adjustments")
        
        # Locations frame
        locations_frame = ttk.LabelFrame(tab, text="Locations")
        locations_frame.pack(fill="both", expand=False, padx=10, pady=10)
        
        # Home location
        ttk.Label(locations_frame, text="Your Home Location:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.home_location_var = tk.StringVar(value="New York")
        home_locations = ttk.Combobox(locations_frame, textvariable=self.home_location_var, 
                                      values=list(self.skincare_companion.get_climate_data("New York").keys()))
        home_locations.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        # Destination location
        ttk.Label(locations_frame, text="Travel Destination:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.destination_location_var = tk.StringVar(value="Miami")
        destination_locations = ttk.Combobox(locations_frame, textvariable=self.destination_location_var, 
                                            values=list(self.skincare_companion.get_climate_data("New York").keys()))
        home_locations["values"] = list(self.skincare_companion.get_climate_data("New York").keys())
        destination_locations["values"] = list(self.skincare_companion.get_climate_data("New York").keys())
        destination_locations.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        
        # Button to adjust routine
        ttk.Button(tab, text="Adjust Routine for Travel", command=self.adjust_for_travel).pack(pady=10)
        
        # Climate comparison
        climate_frame = ttk.LabelFrame(tab, text="Climate Comparison")
        climate_frame.pack(fill="both", expand=False, padx=10, pady=10)
        
        # Table headers
        ttk.Label(climate_frame, text="Factor").grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(climate_frame, text="Home").grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(climate_frame, text="Destination").grid(row=0, column=2, padx=5, pady=5)
        ttk.Label(climate_frame, text="Difference").grid(row=0, column=3, padx=5, pady=5)
        
        # Climate factors
        factors = ["Humidity", "UV Index", "Pollution Index"]
        self.climate_values = {}
        
        for i, factor in enumerate(factors, 1):
            ttk.Label(climate_frame, text=factor).grid(row=i, column=0, padx=5, pady=5)
            
            # Home value
            home_var = tk.StringVar()
            home_label = ttk.Label(climate_frame, textvariable=home_var)
            home_label.grid(row=i, column=1, padx=5, pady=5)
            
            # Destination value
            dest_var = tk.StringVar()
            dest_label = ttk.Label(climate_frame, textvariable=dest_var)
            dest_label.grid(row=i, column=2, padx=5, pady=5)
            
            # Difference
            diff_var = tk.StringVar()
            diff_label = ttk.Label(climate_frame, textvariable=diff_var)
            diff_label.grid(row=i, column=3, padx=5, pady=5)
            
            self.climate_values[factor.lower().replace(" ", "_")] = {
                "home": home_var,
                "destination": dest_var,
                "difference": diff_var
            }
        
        # Results area
        results_frame = ttk.LabelFrame(tab, text="Adjustment Recommendations")
        results_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.climate_text = scrolledtext.ScrolledText(results_frame, height=15, width=80, wrap=tk.WORD)
        self.climate_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Update climate data when locations change
        home_locations.bind("<<ComboboxSelected>>", lambda e: self.update_climate_display())
        destination_locations.bind("<<ComboboxSelected>>", lambda e: self.update_climate_display())
        
        # Initialize climate display
        self.update_climate_display()
    
    def update_product_list(self):
        self.product_listbox.delete(0, tk.END)
        for product in self.products:
            self.product_listbox.insert(tk.END, product["name"])
    
    def load_product_details(self, event):
        selected_indices = self.product_listbox.curselection()
        if selected_indices:
            index = selected_indices[0]
            product = self.products[index]
            self.product_name_var.set(product["name"])
            self.ingredients_var.set(", ".join(product["ingredients"]))
            self.preferred_time_var.set(product["preferred_time"])
    
    def add_product(self):
        name = self.product_name_var.get().strip()
        ingredients_text = self.ingredients_var.get().strip()
        preferred_time = self.preferred_time_var.get()
        
        if not name:
            messagebox.showerror("Error", "Product name is required")
            return
        
        if not ingredients_text:
            messagebox.showerror("Error", "At least one ingredient is required")
            return
        
        # Parse ingredients
        ingredients = [i.strip().lower() for i in ingredients_text.split(",") if i.strip()]
        
        # Add new product
        self.products.append({
            "name": name,
            "ingredients": ingredients,
            "preferred_time": preferred_time
        })
        
        # Update product list
        self.update_product_list()
        
        # Clear form
        self.product_name_var.set("")
        self.ingredients_var.set("")
        self.preferred_time_var.set("both")
    
    def update_product(self):
        selected_indices = self.product_listbox.curselection()
        if not selected_indices:
            messagebox.showerror("Error", "No product selected")
            return
        
        index = selected_indices[0]
        name = self.product_name_var.get().strip()
        ingredients_text = self.ingredients_var.get().strip()
        preferred_time = self.preferred_time_var.get()
        
        if not name:
            messagebox.showerror("Error", "Product name is required")
            return
        
        if not ingredients_text:
            messagebox.showerror("Error", "At least one ingredient is required")
            return
        
        # Parse ingredients
                # Parse ingredients
        ingredients = [i.strip().lower() for i in ingredients_text.split(",") if i.strip()]
        
        # Update the selected product
        self.products[index] = {
            "name": name,
            "ingredients": ingredients,
            "preferred_time": preferred_time
        }
        
        # Update product list
        self.update_product_list()
        
        # Clear form
        self.product_name_var.set("")
        self.ingredients_var.set("")
        self.preferred_time_var.set("both")
    
    def remove_product(self):
        selected_indices = self.product_listbox.curselection()
        if not selected_indices:
            messagebox.showerror("Error", "No product selected")
            return
        
        index = selected_indices[0]
        del self.products[index]
        
        # Update product list
        self.update_product_list()
        
        # Clear form
        self.product_name_var.set("")
        self.ingredients_var.set("")
        self.preferred_time_var.set("both")
    
    def clear_products(self):
        self.products = []
        self.update_product_list()
        
        # Clear form
        self.product_name_var.set("")
        self.ingredients_var.set("")
        self.preferred_time_var.set("both")
    
    def analyze_routine(self):
        if not self.products:
            messagebox.showwarning("No Products", "Please add products to analyze.")
            return
        
        # Perform analysis
        analysis_result = self.skincare_companion.analyze_skincare_routine(self.products)
        
        # Display conflicts
        self.conflicts_text.delete(1.0, tk.END)
        if analysis_result["conflicts"]:
            self.conflicts_text.insert(tk.END, "Found conflicts:\n")
            for conflict in analysis_result["conflicts"]:
                self.conflicts_text.insert(tk.END, 
                    f"- {conflict['product1']} ({conflict['ingredient1']}) conflicts with "
                    f"{conflict['product2']} ({conflict['ingredient2']}). "
                    f"Wait {conflict['waiting_time']} minutes between applications.\n")
        else:
            self.conflicts_text.insert(tk.END, "No conflicts found in your routine!\n")
        
        # Visualize the interaction graph
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
        
        fig = self.skincare_companion.visualize_conflicts(analysis_result)
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def generate_schedule(self):
        if not self.products:
            messagebox.showwarning("No Products", "Please add products to generate a schedule.")
            return
        
        # Generate schedule
        schedule = self.skincare_companion.create_application_schedule(self.products)
        
        # Visualize the schedule
        for widget in self.schedule_frame.winfo_children():
            widget.destroy()
        
        fig = self.skincare_companion.visualize_schedule(schedule)
        canvas = FigureCanvasTkAgg(fig, master=self.schedule_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def update_climate_display(self):
        home_location = self.home_location_var.get()
        destination_location = self.destination_location_var.get()
        
        home_climate = self.skincare_companion.get_climate_data(home_location)
        destination_climate = self.skincare_companion.get_climate_data(destination_location)
        
        # Update climate values
        for factor, vars in self.climate_values.items():
            home_value = home_climate.get(factor, 0)
            dest_value = destination_climate.get(factor, 0)
            difference = dest_value - home_value
            
            vars["home"].set(home_value)
            vars["destination"].set(dest_value)
            vars["difference"].set(difference)
    
    def adjust_for_travel(self):
        if not self.products:
            messagebox.showwarning("No Products", "Please add products to adjust for travel.")
            return
        
        home_location = self.home_location_var.get()
        destination_location = self.destination_location_var.get()
        
        home_climate = self.skincare_companion.get_climate_data(home_location)
        destination_climate = self.skincare_companion.get_climate_data(destination_location)
        
        # Adjust routine for climate
        adjustment_result = self.skincare_companion.adjust_for_climate(
            self.products, home_climate, destination_climate
        )
        
        # Display adjustments
        self.climate_text.delete(1.0, tk.END)
        self.climate_text.insert(tk.END, "Climate Changes:\n")
        for change in adjustment_result["climate_changes"]:
            self.climate_text.insert(tk.END, f"- {change.replace('_', ' ').title()}\n")
        
        self.climate_text.insert(tk.END, "\nAdjustment Recommendations:\n")
        for adj in adjustment_result["adjustments"]:
            if adj["product"]:
                self.climate_text.insert(tk.END, 
                    f"- For {adj['product']} ({adj['ingredient']}): {adj['adjustment']}\n")
            else:
                self.climate_text.insert(tk.END, 
                    f"- {adj['adjustment_type'].title()}: {adj['adjustment']}\n")
if __name__ == "__main__":
    root = tk.Tk()  # Create the root window
    app = SkincareAppGUI(root)  # Instantiate your GUI class
    root.mainloop()  # Start the main event loop

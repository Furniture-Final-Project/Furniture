import json
import os


class InventorySingleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(InventorySingleton, cls).__new__(cls)
        return cls._instance


class Inventory(InventorySingleton):
    def __init__(self, base_data_folder):
        # Only initialize the first time: prevents re-loading on subsequent instantiations.
        if not hasattr(self, 'initialized'):
            # Set paths for each file (all files are stored in the base_data_folder)
            self.furniture_file = os.path.join(base_data_folder, "furniture_data.json")
            self.chairs_file = os.path.join(base_data_folder, "chairs_data.json")
            self.beds_file = os.path.join(base_data_folder, "beds_data.json")
            self.bookshelves_file = os.path.join(base_data_folder, "bookshelves_data.json")
            self.sofas_file = os.path.join(base_data_folder, "sofas_data.json")
            self.tables_file = os.path.join(base_data_folder, "tables_data.json")
            self.inventory_file = os.path.join(base_data_folder, "inventory.json")

            # Load JSON files and store the data
            self.furniture_data = self._load_json(self.furniture_file)
            self.chairs_data = self._load_json(self.chairs_file)
            self.beds_data = self._load_json(self.beds_file)
            self.bookshelves_data = self._load_json(self.bookshelves_file)
            self.sofas_data = self._load_json(self.sofas_file)
            self.tables_data = self._load_json(self.tables_file)
            self.inventory_data = self._load_json(self.inventory_file)

            self.initialized = True

    def _load_json(self, filepath):
        with open(filepath, "r") as file:
            return json.load(file)

    def _lookup_subclass_data(self, category, model_num):
        # Depending on the category, return the subclass data matching model_num.
        if category.lower() == "chair":
            return next((item for item in self.chairs_data if item['model_num'] == model_num), {})
        elif category.lower() == "bed":
            return next((item for item in self.beds_data if item['model_num'] == model_num), {})
        elif category.lower() == "bookshelf":
            return next((item for item in self.bookshelves_data if item['model_num'] == model_num), {})
        elif category.lower() == "sofa":
            return next((item for item in self.sofas_data if item['model_num'] == model_num), {})
        elif category.lower() == "table":
            return next((item for item in self.tables_data if item['model_num'] == model_num), {})
        else:
            return {}

    def get_all_available_items(self):
        """
        Returns a list of items that are available (i.e., quantity > 0).
        For each item in the inventory:
        - It locates the general furniture data using model_num.
        - It locates the subclass-specific data using category and model_num.
        - It then merges the two datasets and includes the quantity from the inventory.
        Assumes that subclass-specific data always exists.
        """
        available_items = []  # Initialize an empty list to hold available items

        for inv_item in self.inventory_data:
            # Process only items with quantity > 0
            if inv_item['quantity'] > 0:
                model_num = inv_item['model_num']  # Get the model number from the inventory record
                category = inv_item['category']  # Get the category (e.g., "Chair", "Table")

                # Lookup the general information for the item from furniture_data using model_num.
                furniture_item = next((item for item in self.furniture_data if item['model_num'] == model_num), {})

                # Lookup the subclass-specific attributes for the item.
                # We assume that this always returns a valid dictionary.
                subclass_item = self._lookup_subclass_data(category, model_num)

                # Merge the general furniture information and subclass-specific details.
                if furniture_item:
                    # Merge the two dictionaries.
                    combined_item = furniture_item.copy()
                    combined_item.update(subclass_item)

                    # Append the fully merged item to our available_items list.
                    available_items.append(combined_item)

        return available_items


# Example usage:
if __name__ == '__main__':
    # Assume that the JSON files are stored under "source/data" folder, so pass that folder path.
    data_folder = os.path.join("source", "data")

    inventory_instance = Inventory(data_folder)
    available_items = inventory_instance.get_all_available_items()

    for item in available_items:
        print(item)
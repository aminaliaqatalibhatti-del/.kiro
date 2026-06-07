"""
Script to add category, travel_style, group_types, trip_duration metadata
to all DESTINATIONS in trip_engine.py.
"""
import re

METADATA = {
    "paris":           {"category":"International Cities","travel_style":["culture","romance","family","solo"],"group_types":["couple","solo","family","friends"],"trip_duration":{"min":3,"ideal":5,"max":10}},
    "tokyo":           {"category":"International Cities","travel_style":["culture","adventure","solo","group"],"group_types":["solo","couple","friends","family"],"trip_duration":{"min":4,"ideal":7,"max":14}},
    "dubai":           {"category":"International Cities","travel_style":["luxury","shopping","adventure","family"],"group_types":["couple","family","friends","solo"],"trip_duration":{"min":3,"ideal":5,"max":7}},
    "bali":            {"category":"Beaches & Coastal","travel_style":["nature","romance","adventure","budget"],"group_types":["couple","solo","friends","family"],"trip_duration":{"min":5,"ideal":8,"max":14}},
    "new york":        {"category":"International Cities","travel_style":["culture","shopping","nightlife","family"],"group_types":["solo","couple","friends","family"],"trip_duration":{"min":4,"ideal":7,"max":10}},
    "istanbul":        {"category":"Historical & Cultural","travel_style":["culture","food","photography","solo"],"group_types":["solo","couple","family","friends"],"trip_duration":{"min":3,"ideal":5,"max":8}},
    "rome":            {"category":"International Cities","travel_style":["culture","history","romance","food"],"group_types":["couple","solo","family","friends"],"trip_duration":{"min":3,"ideal":5,"max":7}},
    "maldives":        {"category":"Beaches & Coastal","travel_style":["luxury","romance","nature","diving"],"group_types":["couple","solo","family"],"trip_duration":{"min":5,"ideal":7,"max":10}},
    "kaghan":          {"category":"Nature & Mountains","travel_style":["nature","adventure","photography","trekking"],"group_types":["solo","friends","couple","family"],"trip_duration":{"min":2,"ideal":4,"max":7}},
    "hunza":           {"category":"Nature & Mountains","travel_style":["nature","adventure","photography","culture"],"group_types":["solo","couple","friends","family"],"trip_duration":{"min":3,"ideal":5,"max":10}},
    "skardu":          {"category":"Nature & Mountains","travel_style":["adventure","trekking","photography","nature"],"group_types":["solo","friends","couple"],"trip_duration":{"min":4,"ideal":7,"max":14}},
    "fairy meadows":   {"category":"Nature & Mountains","travel_style":["adventure","trekking","photography","nature"],"group_types":["solo","friends","couple"],"trip_duration":{"min":2,"ideal":3,"max":5}},
    "naran":           {"category":"Nature & Mountains","travel_style":["nature","photography","adventure","family"],"group_types":["family","couple","friends","solo"],"trip_duration":{"min":2,"ideal":4,"max":6}},
    "swat":            {"category":"Nature & Mountains","travel_style":["nature","history","adventure","photography"],"group_types":["family","couple","friends","solo"],"trip_duration":{"min":2,"ideal":4,"max":7}},
    "murree":          {"category":"Nature & Mountains","travel_style":["nature","family","weekend","photography"],"group_types":["family","couple","friends"],"trip_duration":{"min":1,"ideal":2,"max":4}},
    "neelum valley":   {"category":"Nature & Mountains","travel_style":["nature","adventure","photography","trekking"],"group_types":["solo","friends","couple"],"trip_duration":{"min":3,"ideal":5,"max":8}},
    "lahore":          {"category":"Historical & Cultural","travel_style":["culture","food","history","photography"],"group_types":["solo","couple","family","friends"],"trip_duration":{"min":2,"ideal":4,"max":6}},
    "taxila":          {"category":"Historical & Cultural","travel_style":["history","photography","culture","education"],"group_types":["solo","couple","family"],"trip_duration":{"min":1,"ideal":2,"max":3}},
    "multan":          {"category":"Historical & Cultural","travel_style":["history","culture","religious","shopping"],"group_types":["solo","family","couple"],"trip_duration":{"min":1,"ideal":2,"max":4}},
    "peshawar":        {"category":"Historical & Cultural","travel_style":["history","culture","food","photography"],"group_types":["solo","couple","family"],"trip_duration":{"min":2,"ideal":3,"max":5}},
    "bahawalpur":      {"category":"Historical & Cultural","travel_style":["history","photography","nature","culture"],"group_types":["solo","couple","family"],"trip_duration":{"min":1,"ideal":2,"max":4}},
    "makkah":          {"category":"Religious Tourism","travel_style":["religious","pilgrimage","spiritual"],"group_types":["solo","family","couple","group"],"trip_duration":{"min":3,"ideal":7,"max":14}},
    "madinah":         {"category":"Religious Tourism","travel_style":["religious","pilgrimage","spiritual"],"group_types":["solo","family","couple","group"],"trip_duration":{"min":2,"ideal":5,"max":10}},
    "jerusalem":       {"category":"Religious Tourism","travel_style":["religious","history","culture","photography"],"group_types":["solo","couple","family","group"],"trip_duration":{"min":3,"ideal":5,"max":7}},
    "karachi":         {"category":"Beaches & Coastal","travel_style":["food","culture","shopping","nightlife"],"group_types":["family","friends","solo","couple"],"trip_duration":{"min":2,"ideal":4,"max":6}},
    "gwadar":          {"category":"Beaches & Coastal","travel_style":["nature","adventure","photography","coastal"],"group_types":["solo","friends","couple"],"trip_duration":{"min":2,"ideal":4,"max":6}},
    "antalya":         {"category":"Beaches & Coastal","travel_style":["beach","history","family","nature"],"group_types":["family","couple","friends","solo"],"trip_duration":{"min":4,"ideal":7,"max":10}},
    "abu dhabi":       {"category":"International Cities","travel_style":["luxury","culture","family","adventure"],"group_types":["family","couple","solo","friends"],"trip_duration":{"min":2,"ideal":4,"max":7}},
    "doha":            {"category":"International Cities","travel_style":["luxury","culture","food","shopping"],"group_types":["couple","solo","family","friends"],"trip_duration":{"min":2,"ideal":4,"max":6}},
    "kuala lumpur":    {"category":"International Cities","travel_style":["food","culture","shopping","family"],"group_types":["family","couple","friends","solo"],"trip_duration":{"min":3,"ideal":5,"max":8}},
    "singapore":       {"category":"International Cities","travel_style":["food","culture","family","shopping"],"group_types":["family","couple","friends","solo"],"trip_duration":{"min":3,"ideal":5,"max":7}},
    "bangkok":         {"category":"International Cities","travel_style":["food","culture","nightlife","adventure"],"group_types":["solo","friends","couple","family"],"trip_duration":{"min":3,"ideal":5,"max":8}},
    "seoul":           {"category":"International Cities","travel_style":["food","culture","shopping","nightlife"],"group_types":["solo","couple","friends","family"],"trip_duration":{"min":3,"ideal":5,"max":8}},
    "london":          {"category":"International Cities","travel_style":["culture","history","food","family"],"group_types":["family","couple","solo","friends"],"trip_duration":{"min":4,"ideal":7,"max":10}},
    "barcelona":       {"category":"International Cities","travel_style":["art","food","beach","nightlife"],"group_types":["friends","couple","solo","family"],"trip_duration":{"min":3,"ideal":5,"max":8}},
    "amsterdam":       {"category":"International Cities","travel_style":["culture","art","cycling","nightlife"],"group_types":["couple","friends","solo","family"],"trip_duration":{"min":3,"ideal":4,"max":6}},
    "los angeles":     {"category":"International Cities","travel_style":["entertainment","beach","culture","nightlife"],"group_types":["friends","couple","solo","family"],"trip_duration":{"min":4,"ideal":7,"max":10}},
    "toronto":         {"category":"International Cities","travel_style":["culture","food","family","nature"],"group_types":["family","couple","friends","solo"],"trip_duration":{"min":3,"ideal":5,"max":8}},
    "sydney":          {"category":"International Cities","travel_style":["nature","food","culture","adventure"],"group_types":["family","couple","friends","solo"],"trip_duration":{"min":4,"ideal":7,"max":10}},
    "patagonia":       {"category":"Adventure Destinations","travel_style":["adventure","trekking","photography","nature"],"group_types":["solo","friends","couple"],"trip_duration":{"min":7,"ideal":14,"max":21}},
    "interlaken":      {"category":"Adventure Destinations","travel_style":["adventure","luxury","nature","photography"],"group_types":["friends","couple","solo","family"],"trip_duration":{"min":3,"ideal":5,"max":7}},
    "queenstown":      {"category":"Adventure Destinations","travel_style":["adventure","nature","food","photography"],"group_types":["friends","solo","couple","family"],"trip_duration":{"min":4,"ideal":6,"max":10}},
    "banff":           {"category":"Adventure Destinations","travel_style":["nature","photography","adventure","family"],"group_types":["family","couple","friends","solo"],"trip_duration":{"min":4,"ideal":7,"max":10}},
    "monaco":          {"category":"Luxury Destinations","travel_style":["luxury","nightlife","food","culture"],"group_types":["couple","solo","friends"],"trip_duration":{"min":2,"ideal":3,"max":5}},
    "santorini":       {"category":"Luxury Destinations","travel_style":["luxury","romance","photography","nature"],"group_types":["couple","solo","family","friends"],"trip_duration":{"min":4,"ideal":7,"max":10}},
    "swiss alps":      {"category":"Luxury Destinations","travel_style":["luxury","adventure","nature","photography"],"group_types":["couple","family","friends","solo"],"trip_duration":{"min":5,"ideal":7,"max":14}},
    "bora bora":       {"category":"Luxury Destinations","travel_style":["luxury","romance","diving","nature"],"group_types":["couple","solo","family"],"trip_duration":{"min":5,"ideal":7,"max":10}},
    "kyoto":           {"category":"Historical & Cultural","travel_style":["culture","history","photography","food"],"group_types":["solo","couple","family","friends"],"trip_duration":{"min":3,"ideal":5,"max":8}},
    "prague":          {"category":"Historical & Cultural","travel_style":["history","culture","nightlife","photography"],"group_types":["couple","friends","solo","family"],"trip_duration":{"min":3,"ideal":4,"max":6}},
    "cairo":           {"category":"Historical & Cultural","travel_style":["history","culture","photography","adventure"],"group_types":["solo","couple","family","friends"],"trip_duration":{"min":3,"ideal":5,"max":8}},
    "cape town":       {"category":"Adventure Destinations","travel_style":["nature","adventure","food","photography"],"group_types":["solo","couple","friends","family"],"trip_duration":{"min":5,"ideal":7,"max":10}},
    "marrakech":       {"category":"Historical & Cultural","travel_style":["culture","food","shopping","photography"],"group_types":["solo","couple","friends","family"],"trip_duration":{"min":3,"ideal":5,"max":7}},
    "vienna":          {"category":"International Cities","travel_style":["culture","music","art","food"],"group_types":["couple","solo","family","friends"],"trip_duration":{"min":3,"ideal":4,"max":6}},
    "lisbon":          {"category":"International Cities","travel_style":["culture","food","nightlife","photography"],"group_types":["solo","couple","friends","family"],"trip_duration":{"min":3,"ideal":5,"max":7}},
    "florence":        {"category":"Historical & Cultural","travel_style":["art","history","food","photography"],"group_types":["couple","solo","family","friends"],"trip_duration":{"min":2,"ideal":4,"max":6}},
    "athens":          {"category":"Historical & Cultural","travel_style":["history","culture","food","photography"],"group_types":["couple","solo","family","friends"],"trip_duration":{"min":3,"ideal":5,"max":7}},
    "rio de janeiro":  {"category":"International Cities","travel_style":["nature","nightlife","culture","adventure"],"group_types":["friends","couple","solo","family"],"trip_duration":{"min":4,"ideal":7,"max":10}},
    "new zealand south island":{"category":"Adventure Destinations","travel_style":["adventure","nature","photography","trekking"],"group_types":["solo","friends","couple","family"],"trip_duration":{"min":7,"ideal":14,"max":21}},
    "iceland":         {"category":"Adventure Destinations","travel_style":["nature","adventure","photography","northern lights"],"group_types":["couple","solo","friends","family"],"trip_duration":{"min":5,"ideal":8,"max":12}},
    "phuket":          {"category":"Beaches & Coastal","travel_style":["beach","nightlife","adventure","food"],"group_types":["friends","couple","solo","family"],"trip_duration":{"min":4,"ideal":7,"max":10}},
}

path = r"c:\Users\angry\OneDrive\Desktop\rabia\backend\backend\trip_engine.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

already_has_category = '"category"' in content
print(f"File already has 'category' field: {already_has_category}")

# Count how many destinations already have category
count = content.count('"category":')
print(f"Destinations with category already: {count}")

for dest_key, meta in METADATA.items():
    # Skip paris - already done
    if dest_key == "paris":
        continue
    
    # Build the search pattern - find the destination key + country line
    # and inject metadata after the climate line
    # Pattern: find '"climate": "...", "best_months": [...],'
    # and replace with '"climate": "...", "best_months": [...],\n        "category": ...'
    
    # Check if this destination already has the fields
    dest_section = f'"{dest_key}":'
    idx = content.find(dest_section)
    if idx == -1:
        print(f"  SKIP: {dest_key} not found in file")
        continue
    
    # Find the climate line for this destination
    climate_idx = content.find('"climate":', idx)
    if climate_idx == -1 or climate_idx > idx + 2000:
        print(f"  SKIP: {dest_key} climate not found nearby")
        continue
    
    # Check if category already added to this destination's block  
    # Find the end of this destination's best_months line
    best_months_idx = content.find('"best_months":', climate_idx)
    if best_months_idx == -1 or best_months_idx > climate_idx + 500:
        print(f"  SKIP: {dest_key} best_months not found nearby")
        continue
    
    # Find end of best_months line
    eol = content.find('\n', best_months_idx)
    line_content = content[best_months_idx:eol]
    
    # Check if category is already right after
    after = content[eol:eol+200]
    if '"category"' in after[:100]:
        print(f"  SKIP: {dest_key} already has category")
        continue
    
    # Build insertion text
    indent = "        "
    category_line = f'\n{indent}"category": "{meta["category"]}",'
    travel_style_line = f'\n{indent}"travel_style": {meta["travel_style"]},'
    group_types_line = f'\n{indent}"group_types": {meta["group_types"]},'
    trip_duration_line = f'\n{indent}"trip_duration": {{"min": {meta["trip_duration"]["min"]}, "ideal": {meta["trip_duration"]["ideal"]}, "max": {meta["trip_duration"]["max"]}}},'
    
    insertion = category_line + travel_style_line + group_types_line + trip_duration_line
    
    content = content[:eol] + insertion + content[eol:]
    print(f"  ADDED: {dest_key}")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("\nDone!")

# Verify
with open(path, "r", encoding="utf-8") as f:
    new_content = f.read()
count_after = new_content.count('"category":')
print(f"Destinations with category after update: {count_after}")

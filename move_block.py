with open('streamlit_app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the start of the block
start_idx = -1
end_idx = -1
for i, line in enumerate(lines):
    if 'if menu == "🎯 SSV Spot Checker":' in line and 'points = []' in lines[i-2]:
        start_idx = i - 2
    if start_idx != -1 and i > start_idx + 10 and 'st.markdown(\'<div class="glass-card">\', unsafe_allow_html=True)' in line:
        end_idx = i
        break

if start_idx != -1 and end_idx != -1:
    block_to_move = lines[start_idx:end_idx]
    
    # We want to insert this block BEFORE the selectbox container
    insert_target_idx = -1
    for i, line in enumerate(lines):
        if '# TOOL KONTROL (CENTERED)' in line:
            insert_target_idx = i + 2
            break
            
    if insert_target_idx != -1:
        # First remove the old block
        del lines[start_idx:end_idx]
        
        # Now insert the block
        # We need to fix the indentation. The old block has 4 spaces indent for 'points = []', let's remove 4 spaces.
        new_block = []
        for line in block_to_move:
            if line.startswith('    '):
                new_block.append(line[4:])
            else:
                new_block.append(line)
        
        lines = lines[:insert_target_idx] + new_block + lines[insert_target_idx:]
        
        # Change expanded=True to expanded=False
        for i, line in enumerate(lines):
            if 'with st.expander("💡 Cara Penggunaan (How it works)", expanded=True):' in line:
                lines[i] = line.replace('expanded=True', 'expanded=False')
        
        with open('streamlit_app.py', 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print('Successfully moved the block!')
    else:
        print('Could not find insert target')
else:
    print('Could not find block to move', start_idx, end_idx)

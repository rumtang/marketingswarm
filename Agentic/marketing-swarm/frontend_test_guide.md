# Frontend Testing Guide for Marketing Swarm

## 🧪 Manual Testing Checklist

Please test these scenarios in your browser at http://localhost:3001:

### 1. Initial Page Load
- [ ] Page loads without errors
- [ ] You see the main conversation interface
- [ ] No console errors (Open Developer Tools with F12)

### 2. Start a Conversation
Try this query: **"How should we launch our new robo-advisor to compete with Betterment?"**

Expected behavior:
- [ ] Agents start responding one by one
- [ ] You see personality-driven responses with specific metrics
- [ ] Responses include industry data (e.g., "$400 CAC", "McKinsey research")
- [ ] Some agents interrupt or challenge others
- [ ] Professional language throughout

### 3. Check Dynamic Features
Look for:
- [ ] **Thinking indicators** before each response
- [ ] **Variable timing** between responses (not all the same)
- [ ] **Conflicts** - agents disagreeing professionally
- [ ] **Building on ideas** - agents referencing each other

### 4. Professional Synthesis
After conversation completes:
- [ ] Executive summary appears
- [ ] Key recommendations listed
- [ ] Risk assessment provided
- [ ] Success metrics defined
- [ ] Implementation roadmap shown

### 5. System Status
Click "Dev Console" button (if available):
- [ ] Shows connection status
- [ ] Displays agent health
- [ ] No error messages

## 🔍 What to Report Back

Please let me know:
1. Which steps passed/failed
2. Any error messages you see
3. If the conversation felt natural and professional
4. Any unexpected behavior

## 🛠️ Quick Fixes

If you encounter issues:

**Nothing loads:**
```bash
# Check if services are running
curl http://localhost:8001/api/health
curl http://localhost:3001
```

**No agent responses:**
```bash
# Check browser console for WebSocket errors
# Should see "WebSocket connected" message
```

**Errors in console:**
```bash
# Take a screenshot or copy the error text
```
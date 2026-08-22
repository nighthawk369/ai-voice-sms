# 🔐 GitHub Secrets - Exact Step-by-Step Instructions

## Method 1: Via Repository Settings (Most Common)

### Step 1: Go to Your Repository
1. Open: https://github.com/nighthawk369/callsync
2. You're now on the repository home page

### Step 2: Click Settings
- Look at the **top navigation bar**
- You should see: Code | Issues | Pull requests | Actions | **Settings**
- Click **Settings** (far right)

### Step 3: Find Secrets in Left Sidebar
Once in Settings page, look at the **left sidebar**. You should see:
- General
- Collaborators
- Moderation options
- Code and automation
  - **Secrets and variables** ← Click this
  - Actions ← This one!
  - Dependabot

**If you see "Secrets and variables":**
Click it → then click **"Actions"** tab

**If you DON'T see "Secrets and variables":**
Scroll down in the left sidebar - it's under "Code and automation" section

### Step 4: You Should See This Screen
You're now in: **Settings → Secrets and variables → Actions**

At the top, there's a button: **"New repository secret"** (green button)

### Step 5: Add First Secret
1. Click **"New repository secret"**
2. Name: `AWS_ACCESS_KEY_ID`
3. Value: (paste your AKIA... from `cat ~/.aws/credentials`)
4. Click **"Add secret"**

### Step 6: Add Second Secret
1. Click **"New repository secret"** again
2. Name: `AWS_SECRET_ACCESS_KEY`
3. Value: (paste your wJal... from `cat ~/.aws/credentials`)
4. Click **"Add secret"**

### Step 7: Add Third Secret
1. Click **"New repository secret"** again
2. Name: `AWS_REGION`
3. Value: `us-east-1`
4. Click **"Add secret"**

### Result
You should now see 3 secrets listed:
- ✓ AWS_ACCESS_KEY_ID
- ✓ AWS_SECRET_ACCESS_KEY
- ✓ AWS_REGION

---

## Method 2: Direct URL (Fastest)

Go directly to this URL (replace `yourusername` and `callsync` with your actual values):

```
https://github.com/nighthawk369/callsync/settings/secrets/actions
```

You should immediately see the "New repository secret" button.

---

## Method 3: If You STILL Can't Find It

### Check 1: Are you an Admin?
You need **Admin** or **Maintain** role on the repo to see Secrets.
- Check: Settings → Collaborators (what's your role?)

### Check 2: Is GitHub Actions Enabled?
1. Go to: Settings → **Actions** → **General**
2. Make sure you see:
   - "Actions permissions" with option selected
   - Select: "Allow all actions and reusable workflows"
3. Click **Save**

### Check 3: Try a Different Browser
Sometimes the sidebar doesn't load. Try:
- Refresh the page (Cmd+R)
- Use incognito/private mode
- Try a different browser

### Check 4: GitHub UI Changed
If GitHub redesigned the interface:
- Go to https://github.com/nighthawk369/callsync
- Press `?` key (opens keyboard shortcuts)
- Search for "Secrets"
- Follow the link

---

## Exact Visual Walkthrough

### What You Should See at Each Step:

**Step 1: Repository Page**
```
GitHub logo | Code Issues Pull requests Actions Settings
[Your repo name: nighthawk369/callsync]
```

**Step 2: After Clicking Settings**
```
Settings page with left sidebar:
General
Collaborators
...
Code and automation  ← Expand this section
  ├─ Webhooks
  ├─ Apps
  └─ Secrets and variables  ← Click this
      ├─ Actions
      ├─ Dependabot
```

**Step 3: After Clicking Secrets and variables → Actions**
```
Settings / Secrets and variables / Actions

[New repository secret] button

Your secrets:
(empty list initially)
```

**Step 4: After Adding Secrets**
```
Settings / Secrets and variables / Actions

[New repository secret] button

Your secrets:
AWS_ACCESS_KEY_ID (Updated X minutes ago)
AWS_REGION (Updated X minutes ago)  
AWS_SECRET_ACCESS_KEY (Updated X minutes ago)
```

---

## Common Issues & Solutions

### "I see 'Secrets and variables' but no 'Actions' tab"

**Solution:**
```
Secrets and variables has 2 tabs:
- Actions  ← Click this one
- Dependabot
```

Make sure you're on the **Actions** tab, not Dependabot.

### "I only see 'Settings' but no left sidebar"

**Solution:**
1. Scroll down
2. The sidebar might be collapsed
3. Or try the direct URL:
   https://github.com/nighthawk369/callsync/settings/secrets/actions

### "Secrets and variables doesn't exist"

**Solution:**
This means GitHub Actions is disabled. Enable it:
1. Settings → **Actions** → **General**
2. Select "Allow all actions and reusable workflows"
3. Save
4. Go back to Secrets and variables

### "New repository secret button is grayed out"

**Solution:**
You don't have admin permissions. Ask the repo owner to add the secrets, or:
1. Go to Settings → Collaborators
2. Check your role (need Admin or Maintain)

---

## Quick Check: Are Secrets Added?

Once secrets are added, you should see them here:
```
https://github.com/nighthawk369/callsync/settings/secrets/actions
```

You should see a list of 3 secrets (names only, not values):
- AWS_ACCESS_KEY_ID
- AWS_REGION
- AWS_SECRET_ACCESS_KEY

(The actual values are hidden for security)

---

## Verify GitHub Actions Can See Secrets

After adding secrets, verify GitHub Actions can access them:

1. Create a test workflow or push to GitHub
2. Go to **Actions** tab (top menu)
3. Click the latest workflow
4. If you see "Configure AWS credentials" step:
   - ✓ If it says "✓ Successfully authenticated"
   - ✗ If it says error, secrets are missing/wrong

---

## Still Stuck?

Try this exact URL path:

**For your repo:**
```
https://github.com/nighthawk369/callsync/settings/secrets/actions
```

This should take you directly to where you can add secrets.

If this URL doesn't work, your repo might not have GitHub Actions enabled yet. Enable it:
```
https://github.com/nighthawk369/callsync/settings/actions
```

---

## GitHub UI Variations

### Old GitHub Interface (pre-2023):
Settings → Secrets → Actions

### New GitHub Interface (2023+):
Settings → Secrets and variables → Actions

### Mobile GitHub (if using phone):
Same steps but might look different. Recommend using desktop browser.

---

**Still having issues?** Let me know:
1. Can you see the Settings page?
2. Can you see the left sidebar?
3. What's the last visible option in the sidebar?

Share a screenshot and I'll help! 📸

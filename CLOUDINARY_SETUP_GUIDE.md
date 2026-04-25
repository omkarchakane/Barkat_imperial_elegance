# Cloudinary Setup Guide for Render Deployment

## Why Cloudinary?

✅ **25 GB free storage** (vs AWS S3's 5 GB)  
✅ **Unlimited uploads/downloads** (no request limits)  
✅ **Auto image optimization** (compresses images automatically)  
✅ **Free forever** (no expiration for students)  
✅ **Easy setup** (2 minutes)

---

## Step 1: Create Cloudinary Account

1. Go to [Cloudinary.com](https://cloudinary.com/users/register/free)
2. Sign up with email (free account)
3. Confirm your email
4. Go to your Dashboard

---

## Step 2: Get Your Cloudinary URL

1. On your Cloudinary Dashboard, you'll see your **API Environment variable**
2. It looks like:
   ```
   cloudinary://YOUR_API_KEY:YOUR_API_SECRET@YOUR_CLOUD_NAME
   ```
3. **Copy the entire URL** (you'll need it next)

---

## Step 3: Add to Render Environment Variables

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Select your web service
3. Click **Environment** tab
4. Click **Add Environment Variable**
5. Name: `CLOUDINARY_URL`
6. Value: Paste the URL from Step 2
7. Click **Save**
8. Add another variable:
   - Name: `USE_CLOUDINARY`
   - Value: `true`
   - Click **Save**

Your environment should now have:
```
DATABASE_URL=postgresql://...  (Supabase)
CLOUDINARY_URL=cloudinary://...
USE_CLOUDINARY=true
```
```

---

## Step 4: Deploy

1. Commit and push:
   ```bash
   git add requirements.txt barkat/settings.py
   git commit -m "Switch from AWS S3 to Cloudinary for free image storage"
   git push origin main
   ```

2. Render will automatically redeploy

3. Migrations run automatically (via Procfile)

---

## Step 5: Test

1. Go to your admin panel: `https://your-site/admin`
2. Login (create superuser if needed)
3. Add a new product with an image
4. Verify the image uploads and displays correctly
5. Wait 30 minutes (Render may restart)
6. Refresh page - image should still load ✓

---

## Local Development (Still Works!)

Your code supports both:
- **Production (USE_CLOUDINARY=true)**: Uploads to Cloudinary
- **Development (USE_CLOUDINARY=false)**: Uploads to local `media/` folder

No changes needed for local development!

---

## Cloudinary Dashboard Features

Once signed up, you can:
- ✅ View all uploaded images
- ✅ Auto-compress images
- ✅ Track storage usage
- ✅ Create API tokens
- ✅ Set up automatic backups

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| **502 error after deploy** | Check Render logs - usually wrong CLOUDINARY_URL |
| **Images not uploading** | Verify `USE_CLOUDINARY=true` is set |
| **Can't see CLOUDINARY_URL** | Go to Cloudinary Dashboard → Settings → API |
| **Storage full** | You have 25 GB free - should be plenty for student project |

---

## Cost

✅ **Forever free** - Cloudinary's free tier never expires

---

## Full Setup Checklist

- [ ] Create Cloudinary account
- [ ] Copy CLOUDINARY_URL from dashboard
- [ ] Add CLOUDINARY_URL to Render environment
- [ ] Set USE_CLOUDINARY=true in Render environment
- [ ] Push code to Render
- [ ] Test by uploading a product with image
- [ ] Verify image persists after app restart

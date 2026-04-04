# Design System Specification: The Nurturing Hearth

## 1. Overview & Creative North Star
**Creative North Star: "The Digital Sanctuary"**

This design system rejects the cold, sterile efficiency of traditional healthcare interfaces in favor of a "Sanctuary" aesthetic. We are building a space that feels like a sun-drenched living room—safe, quiet, and deeply human. 

To achieve this, we move beyond the "template" look by embracing **Organic Editorialism**. This means prioritizing generous whitespace (the "breath" of the UI), intentional asymmetry in layout, and a rejection of the rigid grid. We avoid the clinical "boxed-in" feel by overlapping elements and using tonal depth rather than structural lines. The result is a premium, high-end experience that feels curated rather than manufactured.

---

## 2. Colors & Surface Philosophy
Our palette is rooted in the earth: Sage (`primary`), Terracotta (`secondary`), and Sand (`tertiary`). These are supported by a foundation of cream and off-white to maintain warmth.

### The "No-Line" Rule
**Lines are scars on a clean canvas.** In this system, 1px solid borders for sectioning are strictly prohibited. Boundaries must be defined exclusively through:
*   **Background Shifts:** Transitioning from `surface` to `surface-container-low`.
*   **Tonal Transitions:** Using subtle shifts in the cream/beige spectrum to define edge cases.

### Surface Hierarchy & Nesting
Treat the UI as a series of physical layers—stacked sheets of fine, textured paper.
*   **Base:** `surface` (#fcfaee) – The desk on which everything sits.
*   **Sections:** `surface-container-low` (#f6f4e8) – Defining broad areas of interest.
*   **Focal Points:** `surface-container-highest` (#e5e3d7) – For interactive elements that require immediate attention.

### The "Glass & Gradient" Rule
To add "soul," use subtle, long-form gradients for primary CTAs and Hero sections. Transition from `primary` (#536431) to `primary-container` (#879a61) at a 135-degree angle. For floating navigation or modal overlays, utilize **Glassmorphism**: use `surface-container-lowest` at 85% opacity with a `20px` backdrop-blur to create a "frosted glass" effect that keeps the user grounded in their current context.

---

## 3. Typography: The Editorial Voice
We use a high-contrast scale to create an authoritative yet gentle hierarchy.

*   **The Anchor (Noto Serif):** Used for `display` and `headline` tiers. This serif provides a sense of history, reliability, and "the written word." It signals that the information is trustworthy and human-reviewed.
*   **The Guide (Plus Jakarta Sans):** Used for `title`, `body`, and `labels`. This sans-serif is geometric but friendly, ensuring maximum legibility for complex healthcare data without feeling robotic.

**Key Rule:** Headlines should never feel crowded. Use a `-0.02em` letter-spacing for `display-lg` to create a tight, high-end editorial look.

---

## 4. Elevation & Depth
Depth is emotional. We use **Tonal Layering** to convey hierarchy, avoiding the "floating button" clichés of the early 2010s.

### The Layering Principle
Place `surface-container-lowest` (#ffffff) cards onto a `surface-container-low` (#f6f4e8) background. The subtle 2% shift in brightness provides all the separation needed for a sophisticated eye.

### Ambient Shadows
Shadows are used sparingly and must mimic natural light:
*   **The Soft Lift:** `box-shadow: 0 12px 32px -4px rgba(27, 28, 21, 0.06);`
*   The shadow color is never grey; it is a tinted version of `on-surface`.

### The "Ghost Border" Fallback
If a border is required for accessibility (e.g., in high-contrast modes), use a **Ghost Border**: `outline-variant` (#c6c8b8) at **15% opacity**. High-contrast, 100% opaque borders are strictly forbidden.

---

## 5. Components

### Buttons & Interaction
*   **Primary:** A gradient of `primary` to `primary-container`. `xl` roundedness (3rem). These should feel like smooth river stones.
*   **Secondary:** `secondary-container` (#fdb38f) with `on-secondary-container` (#784327) text. Use for supportive family-oriented actions.
*   **Ghost States:** No background, `primary` text, and a "Ghost Border" on hover.

### Inputs & Fields
*   **Form Fields:** Use `surface-container-high` (#eae8dd) as the fill color. No bottom border. Large `md` (1.5rem) corner radius.
*   **Focus State:** A soft 4px outer glow of `primary-fixed` (#d5ebaa) rather than a sharp stroke.

### Cards & Navigation
*   **The No-Divider Rule:** Forbid the use of horizontal rules (`<hr>`). Separate list items using `1.5rem` of vertical whitespace or a subtle background toggle between `surface` and `surface-container-low`.
*   **Nurture Cards:** Used for health tips. Use `tertiary-container` (#a39172) with `lg` (2rem) rounded corners and an asymmetrical padding (e.g., `top: 2rem, left: 2rem, right: 3rem, bottom: 2rem`) to create an editorial feel.

### Specialized Components
*   **The Family Hub Chip:** A large, pill-shaped avatar group with `full` roundedness, using `primary-fixed` backgrounds to denote active family members being managed.
*   **Timeline Blossoms:** Instead of a clinical vertical line for medical history, use a series of soft, overlapping circles in varying shades of `sage` and `terracotta` to show the progression of care.

---

## 6. Do's and Don'ts

### Do:
*   **Embrace Asymmetry:** Place a heading on the left and a supportive "Nurture Card" slightly offset to the right.
*   **Use Generous Leading:** Increase line-height in body text (1.6 or 1.7) to ensure the interface feels "calm" and readable for all ages.
*   **Layer Surfaces:** Think of the UI as physical paper. Use `surface-dim` for transitions.

### Don't:
*   **Don't use "True Black":** Use `on-surface` (#1b1c15) for text. True black is too harsh for a nurturing environment.
*   **Don't use Square Corners:** Even "small" components like checkboxes should have a minimum `sm` (0.5rem) radius.
*   **Don't Over-shadow:** If three elements are on a page, only one (the primary action) should have an ambient shadow. Let the others sit flat on their tonal layers.
*   **Don't use Clinical Blues:** If you need to denote "Information," use `tertiary` (warm earth tones), never a standard blue.
#code <!DOCTYPE html>

<html class="light" lang="en"><head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif:wght@400;600;700&amp;family=Plus+Jakarta+Sans:wght@400;500;600;700&amp;display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&amp;display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&amp;display=swap" rel="stylesheet"/>
<script id="tailwind-config">
      tailwind.config = {
        darkMode: "class",
        theme: {
          extend: {
            "colors": {
                    "primary-fixed": "#d5ebaa",
                    "surface-container-low": "#f6f4e8",
                    "primary": "#536431",
                    "surface-container": "#f0eee2",
                    "primary-container": "#879a61",
                    "on-secondary-container": "#784327",
                    "surface-dim": "#dcdacf",
                    "inverse-primary": "#b9ce90",
                    "surface-tint": "#536431",
                    "secondary-fixed-dim": "#ffb693",
                    "error": "#ba1a1a",
                    "secondary": "#895033",
                    "tertiary-fixed-dim": "#d8c4a2",
                    "tertiary-fixed": "#f5e0bd",
                    "on-background": "#1b1c15",
                    "inverse-on-surface": "#f3f1e5",
                    "on-primary": "#ffffff",
                    "primary-fixed-dim": "#b9ce90",
                    "surface": "#fcfaee",
                    "on-secondary": "#ffffff",
                    "secondary-fixed": "#ffdbcc",
                    "secondary-container": "#fdb38f",
                    "tertiary-container": "#a39172",
                    "surface-container-highest": "#e5e3d7",
                    "on-error": "#ffffff",
                    "background": "#fcfaee",
                    "on-surface": "#1b1c15",
                    "on-primary-fixed": "#131f00",
                    "on-tertiary-fixed": "#241a05",
                    "error-container": "#ffdad6",
                    "surface-container-high": "#eae8dd",
                    "on-tertiary-container": "#362a13",
                    "on-tertiary": "#ffffff",
                    "on-tertiary-fixed-variant": "#52452b",
                    "outline": "#76786b",
                    "on-secondary-fixed": "#351000",
                    "surface-variant": "#e5e3d7",
                    "on-surface-variant": "#46483c",
                    "on-primary-fixed-variant": "#3c4c1c",
                    "on-secondary-fixed-variant": "#6c391e",
                    "surface-bright": "#fcfaee",
                    "inverse-surface": "#303129",
                    "outline-variant": "#c6c8b8",
                    "surface-container-lowest": "#ffffff",
                    "tertiary": "#6b5c41",
                    "on-error-container": "#93000a",
                    "on-primary-container": "#223103"
            },
            "borderRadius": {
                    "DEFAULT": "1rem",
                    "lg": "2rem",
                    "xl": "3rem",
                    "full": "9999px"
            },
            "fontFamily": {
                    "headline": ["Noto Serif"],
                    "body": ["Plus Jakarta Sans"],
                    "label": ["Plus Jakarta Sans"]
            }
          },
        }
      }
    </script>
<style>
        .material-symbols-outlined {
            font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
        }
        body {
            background-color: #fcfaee;
            color: #1b1c15;
            font-family: 'Plus Jakarta Sans', sans-serif;
        }
    </style>
</head>
<body class="flex min-h-screen">
<!-- SideNavBar -->
<aside class="flex flex-col h-full py-8 px-6 bg-[#f6f4e8] dark:bg-stone-900 h-screen w-72 fixed left-0 top-0 border-r border-[#c6c8b8]/15 z-40">
<div class="mb-10 px-2">
<h1 class="font-['Noto_Serif'] text-lg text-[#536431] dark:text-[#d5ebaa]">Nurturing Navigation</h1>
<p class="font-['Plus_Jakarta_Sans'] text-sm font-medium leading-relaxed opacity-60">Your Digital Sanctuary</p>
</div>
<nav class="flex-1 space-y-1">
<a class="flex items-center gap-3 py-3 px-4 rounded-xl transition-all hover:text-[#536431] dark:hover:text-[#d5ebaa] hover:translate-x-1 text-[#536431] dark:text-[#d5ebaa] font-bold border-r-4 border-[#536431] dark:border-[#d5ebaa] active:scale-95 duration-200" href="#">
<span class="material-symbols-outlined">grid_view</span>
<span class="font-['Plus_Jakarta_Sans'] text-sm font-medium leading-relaxed">Dashboard</span>
</a>
<a class="flex items-center gap-3 py-3 px-4 rounded-xl transition-all hover:text-[#536431] dark:hover:text-[#d5ebaa] hover:translate-x-1 text-stone-600 dark:text-stone-400 opacity-80 active:scale-95 duration-200" href="#">
<span class="material-symbols-outlined">map</span>
<span class="font-['Plus_Jakarta_Sans'] text-sm font-medium leading-relaxed">Care Maze</span>
</a>
<a class="flex items-center gap-3 py-3 px-4 rounded-xl transition-all hover:text-[#536431] dark:hover:text-[#d5ebaa] hover:translate-x-1 text-stone-600 dark:text-stone-400 opacity-80 active:scale-95 duration-200" href="#">
<span class="material-symbols-outlined">medication</span>
<span class="font-['Plus_Jakarta_Sans'] text-sm font-medium leading-relaxed">Medications</span>
</a>
<a class="flex items-center gap-3 py-3 px-4 rounded-xl transition-all hover:text-[#536431] dark:hover:text-[#d5ebaa] hover:translate-x-1 text-stone-600 dark:text-stone-400 opacity-80 active:scale-95 duration-200" href="#">
<span class="material-symbols-outlined">history</span>
<span class="font-['Plus_Jakarta_Sans'] text-sm font-medium leading-relaxed">History</span>
</a>
</nav>
<div class="mt-auto space-y-6">
<button class="w-full bg-gradient-to-br from-[#536431] to-[#879a61] text-white py-4 px-6 rounded-xl font-semibold shadow-sm hover:opacity-90 transition-opacity">
                Request Support
            </button>
<div class="space-y-1">
<a class="flex items-center gap-3 py-2 px-4 rounded-xl text-stone-600 dark:text-stone-400 hover:text-[#536431] transition-colors" href="#">
<span class="material-symbols-outlined">settings</span>
<span class="font-['Plus_Jakarta_Sans'] text-sm">Settings</span>
</a>
<a class="flex items-center gap-3 py-2 px-4 rounded-xl text-stone-600 dark:text-stone-400 hover:text-[#536431] transition-colors" href="#">
<span class="material-symbols-outlined">help_outline</span>
<span class="font-['Plus_Jakarta_Sans'] text-sm">Help</span>
</a>
</div>
</div>
</aside>
<!-- Main Canvas -->
<main class="flex-1 ml-72">
<!-- TopAppBar -->
<header class="flex justify-between items-center px-8 h-20 w-full sticky top-0 z-50 bg-[#fcfaee]/85 dark:bg-stone-900/85 backdrop-blur-md">
<div class="text-2xl font-bold font-['Noto_Serif'] text-[#536431] dark:text-[#d5ebaa]">Care Pulse</div>
<div class="flex items-center gap-6">
<div class="relative group">
<input class="bg-[#f6f4e8] dark:bg-stone-800 border-none rounded-full px-6 py-2 w-64 focus:ring-2 focus:ring-[#d5ebaa] text-sm font-['Plus_Jakarta_Sans']" placeholder="Search your care path..." type="text"/>
<span class="material-symbols-outlined absolute right-4 top-2 text-stone-400">search</span>
</div>
<div class="flex items-center gap-4">
<button class="material-symbols-outlined text-[#536431] hover:bg-[#f6f4e8] p-2 rounded-full transition-colors">notifications</button>
<button class="material-symbols-outlined text-[#536431] hover:bg-[#f6f4e8] p-2 rounded-full transition-colors">favorite</button>
<div class="h-10 w-10 rounded-full overflow-hidden border-2 border-primary-fixed">
<img alt="User profile avatar" class="w-full h-full object-cover" data-alt="Close-up portrait of a kind middle-aged woman with a warm smile in a sunlit room with soft plants in background" src="https://lh3.googleusercontent.com/aida-public/AB6AXuCd5poNP6ksNtz9kugEG2dKf9lidAjU4BK7PwFYzu5d_mpjF9VCuMYQm3kZXfReMq20cXiYmWEV7VCe7SnVwpD7NtyBQSzLgHrb9juA-q5THajYugNXbKFOjS3LjT_vlINUj1FRrzAFUcQKt5QaV7wB5Yo05tTwZaLc-Qdn8L2lhgdSijWaVeF0J_9_C08xW-CUDuieYt-qKQiW6-TjZoNqyewro5TgtB30jkQXC8w-ul5S_H4O8P1MvjQ2GxE-UABFguYMDr9KDBaK"/>
</div>
</div>
</div>
</header>
<!-- Dashboard Content -->
<div class="p-8 max-w-7xl mx-auto">
<!-- Hero / Greeting -->
<section class="mb-12">
<h2 class="font-['Noto_Serif'] text-4xl font-bold tracking-tight text-on-surface mb-4">Good morning, Martha</h2>
<!-- Supportive Note -->
<div class="bg-surface-container-low p-6 rounded-lg flex items-start gap-4 max-w-2xl">
<span class="material-symbols-outlined text-primary text-3xl" style="font-variation-settings: 'FILL' 1;">face</span>
<div>
<p class="font-['Plus_Jakarta_Sans'] text-lg text-primary font-medium italic">"Hi, I've checked your upcoming week—all looks clear for now."</p>
<p class="text-sm text-stone-500 mt-1">Your Personal Care Agent</p>
</div>
</div>
</section>
<!-- Bento Grid Layout -->
<div class="grid grid-cols-12 gap-8">
<!-- Today's Focus (Large Card) -->
<div class="col-span-12 lg:col-span-7 bg-surface-container-lowest rounded-xl p-8 shadow-[0_12px_32px_-4px_rgba(27,28,21,0.06)] flex flex-col justify-between">
<div>
<div class="flex justify-between items-start mb-8">
<h3 class="font-['Noto_Serif'] text-2xl font-semibold">Today's Focus</h3>
<span class="bg-primary-fixed text-on-primary-fixed px-4 py-1 rounded-full text-xs font-bold tracking-wider">PRIORITY</span>
</div>
<div class="space-y-6">
<div class="flex items-center gap-6 p-6 bg-surface-container-low rounded-lg transition-colors hover:bg-surface-container">
<div class="h-14 w-14 bg-secondary-container rounded-full flex items-center justify-center text-on-secondary-container">
<span class="material-symbols-outlined text-3xl">pill</span>
</div>
<div class="flex-1">
<p class="text-xl font-semibold text-on-surface">Refill your Vitamin D</p>
<p class="text-stone-500">Only 3 doses remaining in your current bottle.</p>
</div>
<button class="text-primary font-bold hover:underline">Order Now</button>
</div>
<div class="flex items-center gap-6 p-6 border-l-4 border-primary bg-surface-container-lowest rounded-lg hover:bg-surface-container transition-colors">
<div class="h-14 w-14 bg-primary-fixed rounded-full flex items-center justify-center text-primary">
<span class="material-symbols-outlined text-3xl">calendar_today</span>
</div>
<div class="flex-1">
<p class="text-xl font-semibold text-on-surface">Dr. Miller's appointment</p>
<p class="text-stone-500">Tomorrow at 10:30 AM • Heart &amp; Wellness Center</p>
</div>
<span class="material-symbols-outlined text-stone-300">chevron_right</span>
</div>
</div>
</div>
<div class="mt-12 flex items-center gap-4 text-stone-400 text-sm">
<span class="material-symbols-outlined text-lg">check_circle</span>
<span>Daily check-in complete</span>
</div>
</div>
<!-- Network Status (Tall Card) -->
<div class="col-span-12 lg:col-span-5 bg-surface-container rounded-xl p-8 flex flex-col">
<h3 class="font-['Noto_Serif'] text-2xl font-semibold mb-2">Network Status</h3>
<p class="font-['Plus_Jakarta_Sans'] text-stone-600 mb-8 leading-relaxed">Your healthcare ecosystem is synced and active.</p>
<div class="relative flex-1 py-4">
<!-- Connection Visualization (Abstracted) -->
<div class="space-y-8 relative">
<!-- Pharmacy Node -->
<div class="flex items-center gap-4">
<div class="relative">
<div class="h-16 w-16 bg-white rounded-full flex items-center justify-center shadow-sm z-10 relative">
<span class="material-symbols-outlined text-secondary text-2xl">local_pharmacy</span>
</div>
<div class="absolute top-1/2 left-full w-12 h-0.5 bg-gradient-to-r from-secondary-container to-primary-fixed"></div>
</div>
<div>
<p class="font-bold">Green Cross Pharmacy</p>
<span class="text-xs text-secondary flex items-center gap-1">
<span class="h-1.5 w-1.5 rounded-full bg-secondary"></span> Live Syncing
                                    </span>
</div>
</div>
<!-- Central Hub -->
<div class="ml-12 flex items-center gap-4">
<div class="relative">
<div class="h-20 w-20 bg-primary rounded-full flex items-center justify-center shadow-lg z-10 relative">
<span class="material-symbols-outlined text-white text-3xl">hub</span>
</div>
<div class="absolute -top-8 left-1/2 w-0.5 h-8 bg-primary-fixed"></div>
<div class="absolute -bottom-8 left-1/2 w-0.5 h-8 bg-tertiary-fixed"></div>
</div>
<div>
<p class="font-bold text-primary">Care Pulse Hub</p>
<p class="text-xs text-primary font-medium">All data protected</p>
</div>
</div>
<!-- Hospital Node -->
<div class="flex items-center gap-4">
<div class="relative">
<div class="h-16 w-16 bg-white rounded-full flex items-center justify-center shadow-sm z-10 relative">
<span class="material-symbols-outlined text-tertiary text-2xl">apartment</span>
</div>
<div class="absolute top-1/2 left-full w-12 h-0.5 bg-gradient-to-r from-tertiary-container to-primary-fixed"></div>
</div>
<div>
<p class="font-bold">St. Mary's General</p>
<span class="text-xs text-primary flex items-center gap-1">
<span class="h-1.5 w-1.5 rounded-full bg-primary"></span> Records Updated
                                    </span>
</div>
</div>
</div>
</div>
<button class="w-full mt-8 py-3 px-4 border border-outline-variant rounded-full text-sm font-semibold text-on-surface hover:bg-white transition-colors">
                        View Network Map
                    </button>
</div>
<!-- Your Care Circle (Full Width Horizontal) -->
<div class="col-span-12">
<div class="bg-surface-container-high rounded-xl p-8">
<div class="flex flex-col md:flex-row justify-between items-end md:items-center mb-8 gap-4">
<div>
<h3 class="font-['Noto_Serif'] text-2xl font-semibold">Your Care Circle</h3>
<p class="text-stone-500">The people helping you stay at your best.</p>
</div>
<button class="flex items-center gap-2 text-primary font-bold px-4 py-2 hover:bg-primary-fixed/20 rounded-full transition-colors">
<span class="material-symbols-outlined">add_circle</span> Add Support Member
                            </button>
</div>
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
<!-- Care Member Card -->
<div class="bg-surface p-6 rounded-lg shadow-sm border border-outline-variant/10 hover:-translate-y-1 transition-transform">
<div class="h-16 w-16 rounded-full bg-tertiary-container mb-4 overflow-hidden">
<img alt="Doctor profile" class="w-full h-full object-cover" data-alt="Professional portrait of a male doctor in a white coat with a friendly expression and glasses" src="https://lh3.googleusercontent.com/aida-public/AB6AXuBDYlEtw4mFGQsi7eofsQQ-g44mI69Yh2Fq13xNp-hi3x7eee2w7DCMCw9E1fLMTqIj8DG9hzZQoIORu1MKh0Wi9lCNHdOlkQ6vrsOPui3EA-wHZfJ1yrq8HD2W-TO9bHPVVRBgueKfp5NHxk1mXYXXKWhgY-ru3YzWf0S8FPSn2POZNF74AZX7e9OTJZ83upQEfrR4ANIwyaMQIitWQOom0PlTJgsodfR-sSW_mdrxH5XdorcExgzPOiIZ1hlxMLF-F4xkd6h4lDQt"/>
</div>
<h4 class="font-bold text-lg">Dr. Miller</h4>
<p class="text-sm text-stone-500 mb-4">Primary Care Physician</p>
<div class="flex gap-2">
<button class="p-2 bg-primary-fixed rounded-full text-primary material-symbols-outlined text-sm">chat</button>
<button class="p-2 bg-primary-fixed rounded-full text-primary material-symbols-outlined text-sm">call</button>
</div>
</div>
<!-- Care Member Card -->
<div class="bg-surface p-6 rounded-lg shadow-sm border border-outline-variant/10 hover:-translate-y-1 transition-transform">
<div class="h-16 w-16 rounded-full bg-secondary-container mb-4 overflow-hidden">
<img alt="Specialist profile" class="w-full h-full object-cover" data-alt="Portrait of a female specialist doctor in blue scrubs looking confident and compassionate" src="https://lh3.googleusercontent.com/aida-public/AB6AXuAq7AbAj45K_G7dixPhpJVX6FObY1UroK9LH-m3cij_1UQrR97bCYsB_dKXaOKMYNayfv7xg1JobFhKS6IPNoWMNOb0AhHigvEjHUkM50umFWmbYWvhdEWsdy1TeVYHzANUp6ZMWcbu_ATCDr15u5fRx9qhgeiBvKE0te4yPeK1AT691L5SL-KOvANa9srCAMC9-4eYUUuM22HFAYU3Ek_FlAG-N1A0oHo3XXoG1YdFv9zore6Krmlo79ZIbTvlWgWkSxneJn3xz-UO"/>
</div>
<h4 class="font-bold text-lg">Sarah Jenkins</h4>
<p class="text-sm text-stone-500 mb-4">Physical Therapist</p>
<div class="flex gap-2">
<button class="p-2 bg-primary-fixed rounded-full text-primary material-symbols-outlined text-sm">chat</button>
<button class="p-2 bg-primary-fixed rounded-full text-primary material-symbols-outlined text-sm">call</button>
</div>
</div>
<!-- Care Member Card (Family) -->
<div class="bg-surface p-6 rounded-lg shadow-sm border border-outline-variant/10 hover:-translate-y-1 transition-transform">
<div class="h-16 w-16 rounded-full bg-primary-fixed mb-4 overflow-hidden">
<img alt="Family profile" class="w-full h-full object-cover" data-alt="Portrait of a young man in a casual sweater with a kind smile, representing a family caregiver" src="https://lh3.googleusercontent.com/aida-public/AB6AXuDPwDytvrzmMWB0MUlEz_I-VQiEA01BMa2mw0m0NlCfrbfKHMj43C8GP_dVeS9vVJ2rXBVHFmMWvhGNgFihNyN6TG-ThXUEj7TfnLPjVr7EA2_4kVsi0oyvMvd6wf09UWWw1nRnPN6rLPGWsMTL-uGKPDBTgxVD9VXdUnXx9FTwTWEMbJIvaKBO0h35q1Cfr4PqlpPT9vSqgRSeZg5tNtaWA5LESrwav6i_CrBZnP5fcwRW37xIYoDAIX47_uoflZcmOH8A83ioNaQ4"/>
</div>
<h4 class="font-bold text-lg">David (Son)</h4>
<p class="text-sm text-stone-500 mb-4">Emergency Contact</p>
<div class="flex gap-2">
<button class="p-2 bg-primary-fixed rounded-full text-primary material-symbols-outlined text-sm" style="font-variation-settings: 'FILL' 1;">favorite</button>
<button class="p-2 bg-primary-fixed rounded-full text-primary material-symbols-outlined text-sm">chat</button>
</div>
</div>
<!-- Nurture Card (Supportive Tip) -->
<div class="bg-tertiary-container text-on-tertiary-container p-6 rounded-lg flex flex-col justify-center items-start lg:ml-4">
<span class="material-symbols-outlined text-4xl mb-4">spa</span>
<p class="font-['Plus_Jakarta_Sans'] font-medium leading-relaxed">"Remember to take 10 minutes for yourself today. A short walk in the garden can work wonders."</p>
</div>
</div>
</div>
</div>
</div>
</div>
<!-- Footer / Tonal Transition -->
<footer class="mt-20 p-12 bg-surface-container-low border-t border-outline-variant/10">
<div class="max-w-7xl mx-auto flex flex-col md:flex-row justify-between gap-12">
<div class="max-w-xs">
<h2 class="font-['Noto_Serif'] text-xl font-bold text-primary mb-4">Care Pulse</h2>
<p class="text-sm text-stone-500 leading-relaxed">Providing a digital sanctuary for your health journey. Reliable, human-centered, and always by your side.</p>
</div>
<div class="flex flex-wrap gap-12">
<div>
<p class="font-bold mb-4">Resources</p>
<ul class="text-sm text-stone-500 space-y-2">
<li><a class="hover:text-primary" href="#">Medical Archives</a></li>
<li><a class="hover:text-primary" href="#">Community Support</a></li>
<li><a class="hover:text-primary" href="#">Safety Protocols</a></li>
</ul>
</div>
<div>
<p class="font-bold mb-4">Privacy</p>
<ul class="text-sm text-stone-500 space-y-2">
<li><a class="hover:text-primary" href="#">Data Protection</a></li>
<li><a class="hover:text-primary" href="#">Terms of Care</a></li>
<li><a class="hover:text-primary" href="#">HIPAA Compliance</a></li>
</ul>
</div>
</div>
</div>
<div class="max-w-7xl mx-auto mt-12 pt-8 border-t border-outline-variant/10 text-center text-xs text-stone-400">
                © 2024 Care Pulse. Designed for Peace of Mind.
            </div>
</footer>
</main>
<!-- FAB (Floating Action Button) - Rendered only on Home/Dashboard as per instructions -->
<button class="fixed bottom-8 right-8 h-16 w-16 bg-gradient-to-br from-secondary to-on-secondary-container text-white rounded-full shadow-2xl flex items-center justify-center hover:scale-105 transition-transform z-50">
<span class="material-symbols-outlined text-3xl">emergency</span>
</button>
</body></html>
#code 2
<!DOCTYPE html>

<html lang="en"><head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif:wght@400;600;700&amp;family=Plus+Jakarta+Sans:wght@400;500;600;700&amp;display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&amp;display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&amp;display=swap" rel="stylesheet"/>
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<script id="tailwind-config">
      tailwind.config = {
        darkMode: "class",
        theme: {
          extend: {
            "colors": {
                    "primary-fixed": "#d5ebaa",
                    "surface-container-low": "#f6f4e8",
                    "primary": "#536431",
                    "surface-container": "#f0eee2",
                    "primary-container": "#879a61",
                    "on-secondary-container": "#784327",
                    "surface-dim": "#dcdacf",
                    "inverse-primary": "#b9ce90",
                    "surface-tint": "#536431",
                    "secondary-fixed-dim": "#ffb693",
                    "error": "#ba1a1a",
                    "secondary": "#895033",
                    "tertiary-fixed-dim": "#d8c4a2",
                    "tertiary-fixed": "#f5e0bd",
                    "on-background": "#1b1c15",
                    "inverse-on-surface": "#f3f1e5",
                    "on-primary": "#ffffff",
                    "primary-fixed-dim": "#b9ce90",
                    "surface": "#fcfaee",
                    "on-secondary": "#ffffff",
                    "secondary-fixed": "#ffdbcc",
                    "secondary-container": "#fdb38f",
                    "tertiary-container": "#a39172",
                    "surface-container-highest": "#e5e3d7",
                    "on-error": "#ffffff",
                    "background": "#fcfaee",
                    "on-surface": "#1b1c15",
                    "on-primary-fixed": "#131f00",
                    "on-tertiary-fixed": "#241a05",
                    "error-container": "#ffdad6",
                    "surface-container-high": "#eae8dd",
                    "on-tertiary-container": "#362a13",
                    "on-tertiary": "#ffffff",
                    "on-tertiary-fixed-variant": "#52452b",
                    "outline": "#76786b",
                    "on-secondary-fixed": "#351000",
                    "surface-variant": "#e5e3d7",
                    "on-surface-variant": "#46483c",
                    "on-primary-fixed-variant": "#3c4c1c",
                    "on-secondary-fixed-variant": "#6c391e",
                    "surface-bright": "#fcfaee",
                    "inverse-surface": "#303129",
                    "outline-variant": "#c6c8b8",
                    "surface-container-lowest": "#ffffff",
                    "tertiary": "#6b5c41",
                    "on-error-container": "#93000a",
                    "on-primary-container": "#223103"
            },
            "borderRadius": {
                    "DEFAULT": "1rem",
                    "lg": "2rem",
                    "xl": "3rem",
                    "full": "9999px"
            },
            "fontFamily": {
                    "headline": ["Noto Serif"],
                    "body": ["Plus Jakarta Sans"],
                    "label": ["Plus Jakarta Sans"]
            }
          },
        },
      }
    </script>
<style>
        .care-path {
            stroke-dasharray: 8;
            animation: flow 30s linear infinite;
        }
        @keyframes flow {
            to { stroke-dashoffset: -100; }
        }
        .material-symbols-outlined {
            font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
        }
    </style>
</head>
<body class="bg-surface font-body text-on-surface antialiased">
<!-- Side Navigation Bar -->
<aside class="flex flex-col h-full py-8 px-6 h-screen w-72 fixed left-0 top-0 bg-[#f6f4e8] dark:bg-stone-900 border-r border-[#c6c8b8]/15 z-40">
<div class="mb-12">
<div class="flex items-center gap-3 mb-2">
<div class="w-10 h-10 rounded-full bg-primary-container flex items-center justify-center text-on-primary-container">
<span class="material-symbols-outlined" data-icon="nest_eco_leaf">nest_eco_leaf</span>
</div>
<h1 class="font-['Noto_Serif'] text-lg text-[#536431] dark:text-[#d5ebaa]">Nurturing Navigation</h1>
</div>
<p class="font-['Plus_Jakarta_Sans'] text-sm font-medium leading-relaxed opacity-70">Your Digital Sanctuary</p>
</div>
<nav class="flex-1 space-y-2">
<a class="flex items-center gap-4 py-3 px-4 rounded-xl text-stone-600 dark:text-stone-400 opacity-80 hover:text-[#536431] dark:hover:text-[#d5ebaa] hover:translate-x-1 transition-all" href="#">
<span class="material-symbols-outlined" data-icon="grid_view">grid_view</span>
<span>Dashboard</span>
</a>
<!-- Active Tab: Care Maze -->
<a class="flex items-center gap-4 py-3 px-4 rounded-xl text-[#536431] dark:text-[#d5ebaa] font-bold border-r-4 border-[#536431] dark:border-[#d5ebaa] bg-surface-container-high/50" href="#">
<span class="material-symbols-outlined" data-icon="map">map</span>
<span>Care Maze</span>
</a>
<a class="flex items-center gap-4 py-3 px-4 rounded-xl text-stone-600 dark:text-stone-400 opacity-80 hover:text-[#536431] dark:hover:text-[#d5ebaa] hover:translate-x-1 transition-all" href="#">
<span class="material-symbols-outlined" data-icon="medication">medication</span>
<span>Medications</span>
</a>
<a class="flex items-center gap-4 py-3 px-4 rounded-xl text-stone-600 dark:text-stone-400 opacity-80 hover:text-[#536431] dark:hover:text-[#d5ebaa] hover:translate-x-1 transition-all" href="#">
<span class="material-symbols-outlined" data-icon="history">history</span>
<span>History</span>
</a>
</nav>
<div class="mt-auto pt-8 border-t border-outline-variant/10 space-y-2">
<button class="w-full py-4 px-6 mb-6 bg-gradient-to-br from-primary to-primary-container text-white rounded-xl font-semibold shadow-lg shadow-primary/10 hover:opacity-90 transition-opacity">
                Request Support
            </button>
<a class="flex items-center gap-4 py-2 px-4 text-stone-600 hover:text-primary transition-colors" href="#">
<span class="material-symbols-outlined" data-icon="settings">settings</span>
<span>Settings</span>
</a>
<a class="flex items-center gap-4 py-2 px-4 text-stone-600 hover:text-primary transition-colors" href="#">
<span class="material-symbols-outlined" data-icon="help_outline">help_outline</span>
<span>Help</span>
</a>
</div>
</aside>
<!-- Top App Bar -->
<header class="flex justify-between items-center px-8 h-20 w-[calc(100%-18rem)] ml-72 sticky top-0 z-50 bg-[#fcfaee]/85 dark:bg-stone-900/85 backdrop-blur-md">
<div class="flex items-center gap-4">
<h2 class="font-['Noto_Serif'] font-semibold tracking-tight text-2xl text-[#536431] dark:text-[#d5ebaa]">Care Maze</h2>
</div>
<div class="flex items-center gap-6">
<div class="hidden md:flex items-center bg-surface-container px-4 py-2 rounded-full border-none">
<span class="material-symbols-outlined text-stone-400 mr-2" data-icon="search">search</span>
<input class="bg-transparent border-none focus:ring-0 text-sm w-48" placeholder="Find care details..." type="text"/>
</div>
<div class="flex items-center gap-4">
<button class="p-2 rounded-full hover:bg-[#f6f4e8] transition-colors relative">
<span class="material-symbols-outlined text-[#536431]" data-icon="notifications">notifications</span>
<span class="absolute top-2 right-2 w-2 h-2 bg-secondary rounded-full"></span>
</button>
<button class="p-2 rounded-full hover:bg-[#f6f4e8] transition-colors">
<span class="material-symbols-outlined text-[#536431]" data-icon="favorite">favorite</span>
</button>
<div class="h-10 w-10 rounded-full bg-surface-container-highest overflow-hidden border-2 border-white">
<img alt="User profile avatar" data-alt="Portrait of a friendly smiling woman in her 30s with soft natural lighting and a warm outdoor background" src="https://lh3.googleusercontent.com/aida-public/AB6AXuBjyNfebbUi8TAb-chbg7IKfulR9rdW5uaAp2GlsuRBaGOZglO-bAqwyiKZ5-pxCIR9RoGHAYNDo_1T8h1kiWy9PtB3I_lvNR6C0psn_24Na4O27KQF67IwRSuCVEtA8g9vtv2IA0tD2Sa2ogmD2Ehr-VsBIe0PRWDGVBElP_doB52NNK3KEm5SbPpcub5nGKGnkVYcK3rrWrVxmHGOs4jzY0anBDYOnCNWIozZDBsVdiJTcZ4Ca_C4KOfusFSC8Euabz2WJeM4VroH"/>
</div>
</div>
</div>
</header>
<!-- Main Content Canvas -->
<main class="ml-72 min-h-[calc(100vh-5rem)] p-8">
<!-- Hero Welcome -->
<section class="max-w-6xl mx-auto mb-12">
<div class="flex flex-col md:flex-row justify-between items-end gap-8">
<div class="max-w-2xl">
<h3 class="text-4xl md:text-5xl font-headline font-bold text-primary mb-4 leading-tight">Mapping your path to <span class="italic">wellness</span>.</h3>
<p class="text-lg text-on-surface-variant leading-relaxed">The Care Maze simplifies the complexity of healthcare connections. See your journey, identify gaps, and stay focused on healing while we handle the logistics.</p>
</div>
<div class="bg-tertiary-container/10 p-6 rounded-lg border border-tertiary-container/20 max-w-xs rotate-2 shadow-sm">
<p class="text-tertiary font-medium text-sm italic">"Healing is a matter of time, but it is sometimes also a matter of opportunity."</p>
<p class="text-tertiary text-xs mt-2">— Hippocrates</p>
</div>
</div>
</section>
<!-- The Maze Interactive Map -->
<section class="max-w-6xl mx-auto mb-12 relative h-[500px] bg-surface-container-low rounded-lg overflow-hidden border-none shadow-inner">
<!-- SVG Map Layer -->
<svg class="absolute inset-0 w-full h-full pointer-events-none" fill="none" viewbox="0 0 1000 500" xmlns="http://www.w3.org/2000/svg">
<!-- Soft Flowing Lines -->
<path class="care-path" d="M250 250 C 350 250, 450 150, 550 150" stroke="#879a61" stroke-linecap="round" stroke-width="3"></path>
<path class="opacity-60" d="M550 150 C 650 150, 750 350, 850 350" stroke="#fdb38f" stroke-dasharray="10 10" stroke-width="3"></path>
<path class="care-path opacity-40" d="M850 350 C 750 350, 350 400, 250 250" stroke="#a39172" stroke-linecap="round" stroke-width="2"></path>
</svg>
<!-- Node 1: St. Jude's Hospital -->
<div class="absolute left-[150px] top-[200px] group">
<div class="relative w-24 h-24 flex items-center justify-center bg-white rounded-full shadow-lg border-4 border-primary-fixed cursor-pointer transition-transform hover:scale-105 z-10">
<span class="material-symbols-outlined text-primary text-3xl" data-icon="hospital">local_hospital</span>
</div>
<div class="absolute -bottom-10 left-1/2 -translate-x-1/2 whitespace-nowrap text-center">
<span class="font-bold text-primary text-sm">St. Jude's Hospital</span>
<p class="text-[10px] text-stone-500">Last visit: Oct 12</p>
</div>
</div>
<!-- Node 2: Downtown Pharmacy -->
<div class="absolute left-[500px] top-[100px] group">
<div class="relative w-24 h-24 flex items-center justify-center bg-white rounded-full shadow-lg border-4 border-tertiary-fixed cursor-pointer transition-transform hover:scale-105 z-10">
<span class="material-symbols-outlined text-tertiary text-3xl" data-icon="pharmacy">local_pharmacy</span>
</div>
<div class="absolute -bottom-10 left-1/2 -translate-x-1/2 whitespace-nowrap text-center">
<span class="font-bold text-tertiary text-sm">Downtown Pharmacy</span>
<p class="text-[10px] text-stone-500">Pick up ready</p>
</div>
</div>
<!-- Node 3: Dr. Sarah (Family Doctor) -->
<div class="absolute left-[800px] top-[300px] group">
<div class="relative w-24 h-24 flex items-center justify-center bg-white rounded-full shadow-lg border-4 border-secondary-fixed cursor-pointer transition-transform hover:scale-105 z-10">
<span class="material-symbols-outlined text-secondary text-3xl" data-icon="medical_services">medical_services</span>
</div>
<div class="absolute -bottom-10 left-1/2 -translate-x-1/2 whitespace-nowrap text-center">
<span class="font-bold text-secondary text-sm">Dr. Sarah</span>
<p class="text-[10px] text-stone-500">Next Appt: Nov 05</p>
</div>
</div>
<!-- Gap Detected Component -->
<div class="absolute left-[580px] top-[240px] z-20">
<div class="bg-surface-container-highest/95 backdrop-blur-md p-5 rounded-lg shadow-xl max-w-[280px] border-none -rotate-1">
<div class="flex items-start gap-3 mb-3">
<div class="w-8 h-8 rounded-full bg-error-container flex items-center justify-center text-error shrink-0">
<span class="material-symbols-outlined text-lg" data-icon="warning">warning</span>
</div>
<div>
<h4 class="font-bold text-on-surface text-sm">Gap Detected</h4>
<p class="text-xs text-on-surface-variant leading-relaxed mt-1">Clinical notes from your hospital visit haven't reached Dr. Sarah yet.</p>
</div>
</div>
<button class="w-full py-2.5 bg-secondary text-white rounded-full text-xs font-bold hover:bg-on-secondary-fixed transition-colors">
                        Let's fix this together
                    </button>
</div>
</div>
<!-- Background Decoration (Illustrations) -->
<div class="absolute bottom-8 right-8 opacity-20 w-48 h-48 pointer-events-none">
<img alt="Abstract Zen" class="rounded-full grayscale" data-alt="Soft abstract texture of smooth river stones in shallow water with ripple effects and natural lighting" src="https://lh3.googleusercontent.com/aida-public/AB6AXuAhiVsvYTvBn2v4vcDfRyvDUvMT_daCMp27xkFuhc-yMr695-ynrVdu-SOcq8vaKD8OJ6gJ4OlAq-Z7Ge4OyvmGWsIVfSNjA49JR_FsgYwSEXYI9QPiYeubEmQnYnL_WYNTBDmFxK2OyJLOqPfntPhX5rPakEWwQ8SSo6FxzDIecuJWXdwzoFfCuQuTaDFkXGVEPOAodOF82DIohGb6uMwZ4oS169jx2pqp88UToiuC3DXkmW541x2ESJhIfqPoz4_6N3hjdqdW9tMT"/>
</div>
</section>
<!-- Insights Bento Grid -->
<section class="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-6">
<!-- Journey Progress -->
<div class="md:col-span-2 bg-surface-container-low rounded-lg p-8 flex flex-col justify-between h-[300px]">
<div>
<h5 class="text-primary font-headline text-2xl font-bold mb-2">Healing Milestone</h5>
<p class="text-on-surface-variant max-w-md">You've completed 75% of your post-op recovery protocol. Dr. Sarah's feedback is the final piece of the puzzle.</p>
</div>
<div class="mt-8">
<div class="flex justify-between items-end mb-3">
<span class="text-xs font-bold tracking-wider uppercase text-primary/60">Recovery Velocity</span>
<span class="text-3xl font-headline font-bold text-primary">75%</span>
</div>
<div class="w-full h-3 bg-surface rounded-full overflow-hidden">
<div class="h-full bg-gradient-to-r from-primary to-primary-container rounded-full w-3/4"></div>
</div>
</div>
</div>
<!-- Nurture Card (Asymmetric Padding) -->
<div class="bg-tertiary-container text-on-tertiary-container rounded-lg pt-12 pb-8 px-10 flex flex-col h-[300px]">
<span class="material-symbols-outlined text-4xl mb-4" data-icon="spa">spa</span>
<h5 class="font-headline text-xl font-bold mb-3">Wellness Tip</h5>
<p class="text-sm leading-relaxed mb-6 opacity-90 italic">"Remember to pause and breathe. Navigating healthcare is a marathon, not a sprint."</p>
<div class="mt-auto">
<a class="text-sm font-bold underline underline-offset-4 decoration-2" href="#">Read Guide</a>
</div>
</div>
<!-- Family Hub Chip (Simplified for Layout) -->
<div class="md:col-span-3 bg-surface-container rounded-xl p-4 flex items-center justify-between">
<div class="flex items-center gap-4">
<div class="flex -space-x-4">
<div class="w-12 h-12 rounded-full border-4 border-surface bg-primary-fixed flex items-center justify-center overflow-hidden">
<img alt="Family Member" data-alt="Close-up portrait of a smiling older man with warm expression and soft focus park background" src="https://lh3.googleusercontent.com/aida-public/AB6AXuAmE-ScRpRjd0oPI2Wbi9TjM8WqBS5a9N_koZiOGRVU3eOkuzYpMDJ2pVHj1Q1OWHhbmTcVvZuEd3y13onzskiOYjgfNllMmL13rEYYvlQbjUuVDPbOAE3icnnoncEXZg65q4K_ITkYUjHhn0bow8JoIOC7KduWaruqH1PJ8qFlp7zK-iQrBP_1vn63TjIFLmw4Fe8xdWvP_Vf3mRAueKiPx8klVpxjj9GL9ERS2oN0OvzzsXYguXHN1XP0z8NAS88oD3dJMKAxgu4c"/>
</div>
<div class="w-12 h-12 rounded-full border-4 border-surface bg-secondary-fixed flex items-center justify-center overflow-hidden">
<img alt="Family Member" data-alt="Portrait of a young woman with natural light and a gentle smile wearing an earthy green linen shirt" src="https://lh3.googleusercontent.com/aida-public/AB6AXuAglyAxkW_4tgAYgg6zUXMDwds-KdQ3Sz4He9CZ-K7m_CpwfqA9A_FJwtMYajiIqhuaw1PjpkEFk0zv-S2COEE59uKDNq_6sU8whl-S-VMryuV2srXYGZSKS1S88mtLgUH2qcK72f4z6LEsRpww4WSHoySJulFCm3Meqxfl7_Y71AZdie41eTL5Eit8AR9mL5ODNtHd1oEDPF4iKqj3RoOrXljW3g65AuRq1ywue1J3GxKPm3JBcOSeG3SV_d4icmUwwJBor3S67_CQ"/>
</div>
<div class="w-12 h-12 rounded-full border-4 border-surface bg-surface-container-highest flex items-center justify-center">
<span class="text-xs font-bold">+2</span>
</div>
</div>
<div>
<span class="block font-bold text-sm">Family Care Network</span>
<span class="text-xs text-on-surface-variant">4 members active today</span>
</div>
</div>
<button class="px-6 py-2 rounded-full bg-white text-primary font-bold text-sm shadow-sm hover:shadow-md transition-shadow">
                    Manage Access
                </button>
</div>
</section>
<!-- Timeline Blossoms (Simplified Visualization) -->
<section class="max-w-6xl mx-auto mt-16 mb-20">
<h5 class="font-headline text-2xl font-bold text-primary mb-8 text-center">Historical Context</h5>
<div class="flex justify-center items-center gap-8 relative py-12 overflow-x-auto no-scrollbar">
<div class="shrink-0 flex flex-col items-center">
<div class="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mb-4 transition-transform hover:scale-110">
<div class="w-8 h-8 rounded-full bg-primary/30"></div>
</div>
<span class="text-xs font-bold text-on-surface-variant">July</span>
</div>
<div class="w-16 h-[2px] bg-outline-variant/30"></div>
<div class="shrink-0 flex flex-col items-center">
<div class="w-20 h-20 rounded-full bg-secondary/10 flex items-center justify-center mb-4 transition-transform hover:scale-110">
<div class="w-12 h-12 rounded-full bg-secondary/30"></div>
</div>
<span class="text-xs font-bold text-on-surface-variant">August</span>
</div>
<div class="w-16 h-[2px] bg-outline-variant/30"></div>
<div class="shrink-0 flex flex-col items-center">
<div class="w-28 h-28 rounded-full bg-primary/20 flex items-center justify-center mb-4 transition-transform hover:scale-110">
<div class="w-20 h-20 rounded-full bg-primary/40"></div>
</div>
<span class="text-xs font-bold text-primary font-bold">September</span>
</div>
<div class="w-16 h-[2px] bg-outline-variant/30"></div>
<div class="shrink-0 flex flex-col items-center opacity-40">
<div class="w-16 h-16 rounded-full bg-tertiary/10 flex items-center justify-center mb-4">
<div class="w-8 h-8 rounded-full bg-tertiary/30"></div>
</div>
<span class="text-xs font-bold text-on-surface-variant">October</span>
</div>
</div>
</section>
</main>
</body></html>
#code 3
<!DOCTYPE html>

<html class="light" lang="en"><head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>Care Pulse | Medication Hub</title>
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif:wght@400;600;700;800&amp;family=Plus+Jakarta+Sans:wght@400;500;600;700&amp;display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&amp;display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&amp;display=swap" rel="stylesheet"/>
<script id="tailwind-config">
      tailwind.config = {
        darkMode: "class",
        theme: {
          extend: {
            "colors": {
                    "primary-fixed": "#d5ebaa",
                    "surface-container-low": "#f6f4e8",
                    "primary": "#536431",
                    "surface-container": "#f0eee2",
                    "primary-container": "#879a61",
                    "on-secondary-container": "#784327",
                    "surface-dim": "#dcdacf",
                    "inverse-primary": "#b9ce90",
                    "surface-tint": "#536431",
                    "secondary-fixed-dim": "#ffb693",
                    "error": "#ba1a1a",
                    "secondary": "#895033",
                    "tertiary-fixed-dim": "#d8c4a2",
                    "tertiary-fixed": "#f5e0bd",
                    "on-background": "#1b1c15",
                    "inverse-on-surface": "#f3f1e5",
                    "on-primary": "#ffffff",
                    "primary-fixed-dim": "#b9ce90",
                    "surface": "#fcfaee",
                    "on-secondary": "#ffffff",
                    "secondary-fixed": "#ffdbcc",
                    "secondary-container": "#fdb38f",
                    "tertiary-container": "#a39172",
                    "surface-container-highest": "#e5e3d7",
                    "on-error": "#ffffff",
                    "background": "#fcfaee",
                    "on-surface": "#1b1c15",
                    "on-primary-fixed": "#131f00",
                    "on-tertiary-fixed": "#241a05",
                    "error-container": "#ffdad6",
                    "surface-container-high": "#eae8dd",
                    "on-tertiary-container": "#362a13",
                    "on-tertiary": "#ffffff",
                    "on-tertiary-fixed-variant": "#52452b",
                    "outline": "#76786b",
                    "on-secondary-fixed": "#351000",
                    "surface-variant": "#e5e3d7",
                    "on-surface-variant": "#46483c",
                    "on-primary-fixed-variant": "#3c4c1c",
                    "on-secondary-fixed-variant": "#6c391e",
                    "surface-bright": "#fcfaee",
                    "inverse-surface": "#303129",
                    "outline-variant": "#c6c8b8",
                    "surface-container-lowest": "#ffffff",
                    "tertiary": "#6b5c41",
                    "on-error-container": "#93000a",
                    "on-primary-container": "#223103"
            },
            "borderRadius": {
                    "DEFAULT": "1rem",
                    "lg": "2rem",
                    "xl": "3rem",
                    "full": "9999px"
            },
            "fontFamily": {
                    "headline": ["Noto Serif"],
                    "body": ["Plus Jakarta Sans"],
                    "label": ["Plus Jakarta Sans"]
            }
          },
        },
      }
    </script>
<style>
        .material-symbols-outlined {
            font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
        }
        body {
            background-color: #fcfaee;
            font-family: 'Plus Jakarta Sans', sans-serif;
            color: #1b1c15;
        }
    </style>
</head>
<body class="bg-surface selection:bg-primary-fixed selection:text-on-primary-fixed">
<!-- Top Navigation Bar -->
<header class="flex justify-between items-center px-8 h-20 w-full sticky top-0 z-50 bg-[#fcfaee]/85 dark:bg-stone-900/85 backdrop-blur-md">
<div class="flex items-center gap-8">
<span class="text-2xl font-bold font-['Noto_Serif'] text-[#536431] dark:text-[#d5ebaa]">Care Pulse</span>
<nav class="hidden md:flex gap-6">
<a class="text-stone-500 dark:text-stone-400 hover:bg-[#f6f4e8] dark:hover:bg-stone-800 transition-colors px-3 py-2 rounded-lg font-['Noto_Serif'] font-semibold tracking-tight" href="#">Dashboard</a>
<a class="text-[#536431] dark:text-[#d5ebaa] font-bold px-3 py-2 rounded-lg font-['Noto_Serif'] font-semibold tracking-tight" href="#">Medications</a>
<a class="text-stone-500 dark:text-stone-400 hover:bg-[#f6f4e8] dark:hover:bg-stone-800 transition-colors px-3 py-2 rounded-lg font-['Noto_Serif'] font-semibold tracking-tight" href="#">Care Maze</a>
</nav>
</div>
<div class="flex items-center gap-4">
<div class="hidden sm:flex items-center bg-surface-container-high px-4 py-2 rounded-full gap-2">
<span class="material-symbols-outlined text-outline">search</span>
<input class="bg-transparent border-none focus:ring-0 text-sm w-48" placeholder="Search prescriptions..." type="text"/>
</div>
<span class="material-symbols-outlined p-2 text-[#536431] dark:text-[#d5ebaa] hover:bg-[#f6f4e8] transition-colors rounded-full cursor-pointer">notifications</span>
<span class="material-symbols-outlined p-2 text-[#536431] dark:text-[#d5ebaa] hover:bg-[#f6f4e8] transition-colors rounded-full cursor-pointer">favorite</span>
<img alt="User profile avatar" class="w-10 h-10 rounded-full object-cover border-2 border-primary-fixed" data-alt="Portrait of a kind middle-aged woman with a gentle smile in soft natural morning light" src="https://lh3.googleusercontent.com/aida-public/AB6AXuDqvCe5uAt63EdKkcN1UlZ3RTpskJ15iaQmNTQxL6pjGvfXKkHBhdeEZQYYx14xOz-VfzFsV50ZGDbqo-qfUL45rFhkTNv6KlHGmVfuGvmRbeGosF7xoELNcwnVJ0Bq7srEf1AwE9Eb6PaX7OIkFpp85pDyXGNy4y9zubsVTdqj0NDzB1f7ckZcf2umsI_5Uwj2kBoUPVrbRiiukAZyAK0ljyPBjQ00HenBrlc0dVCJTtWMSwdBpKbw6ermgLOntzynYkJwjteOgQN7"/>
</div>
</header>
<div class="flex">
<!-- Side Navigation Bar -->
<aside class="hidden lg:flex flex-col h-screen w-72 fixed left-0 top-0 pt-24 pb-8 px-6 bg-[#f6f4e8] dark:bg-stone-900 border-r border-[#c6c8b8]/15 z-40">
<div class="mb-10">
<h2 class="font-['Noto_Serif'] text-lg text-[#536431] dark:text-[#d5ebaa] font-bold">Nurturing Navigation</h2>
<p class="text-stone-600 dark:text-stone-400 text-xs opacity-80 uppercase tracking-widest mt-1">Your Digital Sanctuary</p>
</div>
<nav class="flex-1 space-y-2">
<a class="flex items-center gap-4 py-3 px-4 rounded-xl text-stone-600 dark:text-stone-400 opacity-80 hover:text-[#536431] dark:hover:text-[#d5ebaa] hover:translate-x-1 transition-all group font-['Plus_Jakarta_Sans'] text-sm font-medium" href="#">
<span class="material-symbols-outlined">grid_view</span>
                    Dashboard
                </a>
<a class="flex items-center gap-4 py-3 px-4 rounded-xl text-stone-600 dark:text-stone-400 opacity-80 hover:text-[#536431] dark:hover:text-[#d5ebaa] hover:translate-x-1 transition-all group font-['Plus_Jakarta_Sans'] text-sm font-medium" href="#">
<span class="material-symbols-outlined">map</span>
                    Care Maze
                </a>
<a class="flex items-center gap-4 py-3 px-4 rounded-xl text-[#536431] dark:text-[#d5ebaa] font-bold border-r-4 border-[#536431] dark:border-[#d5ebaa] font-['Plus_Jakarta_Sans'] text-sm" href="#">
<span class="material-symbols-outlined" style="font-variation-settings: 'FILL' 1;">medication</span>
                    Medications
                </a>
<a class="flex items-center gap-4 py-3 px-4 rounded-xl text-stone-600 dark:text-stone-400 opacity-80 hover:text-[#536431] dark:hover:text-[#d5ebaa] hover:translate-x-1 transition-all group font-['Plus_Jakarta_Sans'] text-sm font-medium" href="#">
<span class="material-symbols-outlined">history</span>
                    History
                </a>
</nav>
<div class="mt-auto space-y-2 pt-6 border-t border-outline-variant/20">
<button class="w-full bg-gradient-to-br from-primary to-primary-container text-on-primary py-4 rounded-xl font-semibold mb-6 flex items-center justify-center gap-2 hover:shadow-lg transition-shadow">
<span class="material-symbols-outlined text-xl">add_circle</span>
                    Request Support
                </button>
<a class="flex items-center gap-4 py-3 px-4 text-stone-600 font-['Plus_Jakarta_Sans'] text-sm hover:text-primary transition-colors" href="#">
<span class="material-symbols-outlined">settings</span>
                    Settings
                </a>
<a class="flex items-center gap-4 py-3 px-4 text-stone-600 font-['Plus_Jakarta_Sans'] text-sm hover:text-primary transition-colors" href="#">
<span class="material-symbols-outlined">help_outline</span>
                    Help
                </a>
</div>
</aside>
<!-- Main Content Area -->
<main class="flex-1 lg:ml-72 min-h-screen px-4 md:px-12 py-10">
<!-- Header Section -->
<div class="mb-12">
<h1 class="text-4xl md:text-5xl font-headline font-bold text-on-surface tracking-tight leading-tight">Medication &amp; Alternatives Hub</h1>
<p class="text-lg text-on-surface-variant mt-4 max-w-2xl leading-relaxed">Your healing journey is guided by care. Manage your prescriptions and find proactive solutions for your well-being.</p>
</div>
<!-- Dashboard Grid -->
<div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
<!-- Left Column: Medications List -->
<div class="lg:col-span-8 space-y-8">
<div class="flex items-center justify-between">
<h2 class="text-2xl font-headline font-semibold text-primary">Current Prescriptions</h2>
<span class="text-sm font-medium text-tertiary bg-tertiary-fixed px-3 py-1 rounded-full">3 Active</span>
</div>
<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
<!-- Med Card 1 -->
<div class="bg-surface-container-lowest p-8 rounded-lg border border-transparent hover:border-primary-fixed transition-all duration-300 shadow-sm flex flex-col justify-between min-h-[220px]">
<div>
<div class="flex justify-between items-start mb-4">
<div class="bg-primary-fixed/30 p-3 rounded-2xl">
<span class="material-symbols-outlined text-primary text-3xl">pill</span>
</div>
<span class="text-[10px] uppercase tracking-widest font-bold text-primary bg-primary-fixed px-2 py-1 rounded">Heart Health</span>
</div>
<h3 class="text-xl font-headline font-bold text-on-surface">Lisinopril</h3>
<p class="text-on-surface-variant text-sm mt-1">10mg • Once daily (Morning)</p>
</div>
<div class="mt-6 pt-4 border-t border-surface-container-low flex items-center justify-between">
<div class="flex items-center gap-2">
<span class="w-2 h-2 rounded-full bg-error animate-pulse"></span>
<span class="text-xs font-bold text-error">Low Supply (2 days)</span>
</div>
<button class="text-primary font-bold text-sm hover:underline">Details</button>
</div>
</div>
<!-- Med Card 2 -->
<div class="bg-surface-container-lowest p-8 rounded-lg border border-transparent hover:border-primary-fixed transition-all duration-300 shadow-sm flex flex-col justify-between min-h-[220px]">
<div>
<div class="flex justify-between items-start mb-4">
<div class="bg-secondary-fixed/30 p-3 rounded-2xl">
<span class="material-symbols-outlined text-secondary text-3xl">water_drop</span>
</div>
<span class="text-[10px] uppercase tracking-widest font-bold text-secondary bg-secondary-fixed px-2 py-1 rounded">Blood Sugar</span>
</div>
<h3 class="text-xl font-headline font-bold text-on-surface">Metformin</h3>
<p class="text-on-surface-variant text-sm mt-1">500mg • Twice daily (Breakfast/Dinner)</p>
</div>
<div class="mt-6 pt-4 border-t border-surface-container-low flex items-center justify-between">
<div class="flex items-center gap-2">
<span class="w-2 h-2 rounded-full bg-primary"></span>
<span class="text-xs font-medium text-on-surface-variant">Supply OK (24 days)</span>
</div>
<button class="text-primary font-bold text-sm hover:underline">Details</button>
</div>
</div>
<!-- Med Card 3 (Nurture Style) -->
<div class="md:col-span-2 bg-tertiary-container/10 p-8 rounded-lg border border-tertiary-container/20 flex flex-col md:flex-row gap-8 items-center">
<div class="flex-1">
<div class="flex items-center gap-3 mb-4">
<span class="material-symbols-outlined text-tertiary">spa</span>
<span class="text-xs font-bold text-tertiary uppercase tracking-widest">Wellness Tip</span>
</div>
<h3 class="text-xl font-headline font-bold text-on-surface">Atorvastatin</h3>
<p class="text-on-surface-variant mt-2 leading-relaxed">20mg • Take at bedtime. Cholesterol synthesis is highest at night, making this the most effective time for your heart.</p>
<div class="mt-4 flex gap-4">
<span class="text-xs bg-surface px-3 py-1 rounded-full border border-outline-variant/30">Next dose: 9:00 PM</span>
<span class="text-xs bg-surface px-3 py-1 rounded-full border border-outline-variant/30">Refill: June 12</span>
</div>
</div>
<div class="w-full md:w-48 h-48 bg-tertiary-fixed rounded-2xl overflow-hidden shadow-inner">
<img alt="Medication safety" class="w-full h-full object-cover mix-blend-multiply opacity-80" data-alt="Close up of a wooden medicine organizer with soft lighting and green plants in the background" src="https://lh3.googleusercontent.com/aida-public/AB6AXuA34NsqL2gBpSZS-u98Qe3gQNy4wvfbO_4U8dzlE4AI1zti1S3AfNC5SHcDmCvCn8AYf5FkMPTVDPY2B-fYhyt50IOBLGifafNCT1yyXP2dg0YTRBwC2PX6mjejn9UgdQi8c92SLNNL30TJXiJYz6FNNSgVZFa9V07ieMdUlwBdOWOPwMz2_UFcWOOyKYCIRmVR6BBJPwPSZN6-aBKvwridPPKCwZKqdOssYUPTa4-De5EHWzhmuFRkoB3nNgBNKMXnuywTpGDjsZ3t"/>
</div>
</div>
</div>
</div>
<!-- Right Column: Agent Insights & Refills -->
<div class="lg:col-span-4 space-y-8">
<!-- Proactive Refill Section -->
<section class="bg-secondary-container/20 p-8 rounded-lg border-l-4 border-secondary-container shadow-sm">
<div class="flex items-center gap-3 mb-6">
<span class="material-symbols-outlined text-on-secondary-container bg-secondary-container p-2 rounded-full">local_pharmacy</span>
<h2 class="text-xl font-headline font-bold text-on-secondary-container">Proactive Refill</h2>
</div>
<div class="space-y-4">
<p class="text-on-secondary-container leading-relaxed">Your <span class="font-bold">Lisinopril</span> is low.</p>
<div class="bg-surface-container-lowest p-4 rounded-2xl shadow-sm border border-secondary-container/10">
<p class="text-sm text-on-surface leading-relaxed">I've found an alternative at your local <span class="font-bold">CVS (Main St.)</span> if the main pharmacy is out.</p>
<button class="mt-4 w-full bg-secondary text-on-secondary py-3 rounded-full font-bold text-sm hover:bg-on-secondary-fixed transition-colors">Route Refill to CVS</button>
</div>
</div>
</section>
<!-- Agent Insights Section -->
<section class="bg-primary-fixed/20 p-8 rounded-lg shadow-sm">
<div class="flex items-center gap-3 mb-6">
<span class="material-symbols-outlined text-primary bg-primary-fixed p-2 rounded-full" style="font-variation-settings: 'FILL' 1;">smart_toy</span>
<h2 class="text-xl font-headline font-bold text-primary">Agent Insights</h2>
</div>
<div class="space-y-6">
<div class="flex gap-4">
<div class="mt-1">
<span class="material-symbols-outlined text-primary-container">restaurant</span>
</div>
<p class="text-sm text-on-surface-variant leading-relaxed">Taking <span class="font-bold">Metformin</span> with food helps prevent an upset stomach. Try it with your morning yogurt.</p>
</div>
<div class="flex gap-4">
<div class="mt-1">
<span class="material-symbols-outlined text-primary-container">wb_sunny</span>
</div>
<p class="text-sm text-on-surface-variant leading-relaxed">Some medications can increase sun sensitivity. Remember your sun protection if you're out in the garden today!</p>
</div>
</div>
</section>
<!-- Pharmacy Location -->
<div class="rounded-lg overflow-hidden h-64 relative group">
<div class="absolute inset-0 bg-black/10 group-hover:bg-transparent transition-all z-10"></div>
<img alt="Map Location" class="w-full h-full object-cover" data-alt="Minimalist artistic map showing clean street lines and soft pastel green areas for parks" src="https://lh3.googleusercontent.com/aida-public/AB6AXuAaXUUR47HCYJbMqbE_-MxPz-CZd95XA82iW_KFTB2X9yxifEGqqmOd6i2JmDRFIIa2HnRrg3QEyr0e7SDw4RLTbyPghGLtZ2h2hyzZEyFbgX5EmQWixyElVLZEXfe7YMUl4X_1fp5NZsnfEAJZaK2MnDsnHQXZVS3c2pRvJYeu9dSU2uovH6t21TfAwz3Stpgh-m58Yahftb996iJhWJUX2djl99l25nDkxbqBz0XqqOquPO1Q0TafdzAW78t-8Ziw6NIWT7agUrS5"/>
<div class="absolute bottom-4 left-4 right-4 bg-surface/90 backdrop-blur-md p-4 rounded-xl z-20 shadow-lg">
<div class="flex justify-between items-center">
<div>
<p class="text-[10px] font-bold text-primary uppercase">Current Pharmacy</p>
<h4 class="font-headline font-bold text-on-surface">CVS Pharmacy - Main St.</h4>
</div>
<span class="material-symbols-outlined text-primary">directions</span>
</div>
</div>
</div>
</div>
</div>
<!-- Footer Spacing -->
<div class="h-24"></div>
</main>
</div>
<!-- Mobile Navigation Bar -->
<nav class="md:hidden fixed bottom-0 left-0 right-0 h-20 bg-surface-container-low backdrop-blur-lg flex justify-around items-center px-6 z-50 border-t border-outline-variant/10">
<div class="flex flex-col items-center gap-1 text-stone-500">
<span class="material-symbols-outlined">grid_view</span>
<span class="text-[10px] font-bold uppercase tracking-tighter">Dashboard</span>
</div>
<div class="flex flex-col items-center gap-1 text-primary">
<span class="material-symbols-outlined" style="font-variation-settings: 'FILL' 1;">pill</span>
<span class="text-[10px] font-bold uppercase tracking-tighter">Meds</span>
</div>
<div class="bg-primary p-3 rounded-full -translate-y-6 shadow-xl shadow-primary/30 text-white">
<span class="material-symbols-outlined text-3xl">add</span>
</div>
<div class="flex flex-col items-center gap-1 text-stone-500">
<span class="material-symbols-outlined">map</span>
<span class="text-[10px] font-bold uppercase tracking-tighter">Care</span>
</div>
<div class="flex flex-col items-center gap-1 text-stone-500">
<span class="material-symbols-outlined">account_circle</span>
<span class="text-[10px] font-bold uppercase tracking-tighter">Profile</span>
</div>
</nav>
</body></html>
# code 4
<!DOCTYPE html>

<html class="light" lang="en"><head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif:wght@400;600;700;800&amp;family=Plus+Jakarta+Sans:wght@400;500;600;700&amp;display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&amp;display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&amp;display=swap" rel="stylesheet"/>
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<script id="tailwind-config">
      tailwind.config = {
        darkMode: "class",
        theme: {
          extend: {
            "colors": {
                    "primary-fixed": "#d5ebaa",
                    "surface-container-low": "#f6f4e8",
                    "primary": "#536431",
                    "surface-container": "#f0eee2",
                    "primary-container": "#879a61",
                    "on-secondary-container": "#784327",
                    "surface-dim": "#dcdacf",
                    "inverse-primary": "#b9ce90",
                    "surface-tint": "#536431",
                    "secondary-fixed-dim": "#ffb693",
                    "error": "#ba1a1a",
                    "secondary": "#895033",
                    "tertiary-fixed-dim": "#d8c4a2",
                    "tertiary-fixed": "#f5e0bd",
                    "on-background": "#1b1c15",
                    "inverse-on-surface": "#f3f1e5",
                    "on-primary": "#ffffff",
                    "primary-fixed-dim": "#b9ce90",
                    "surface": "#fcfaee",
                    "on-secondary": "#ffffff",
                    "secondary-fixed": "#ffdbcc",
                    "secondary-container": "#fdb38f",
                    "tertiary-container": "#a39172",
                    "surface-container-highest": "#e5e3d7",
                    "on-error": "#ffffff",
                    "background": "#fcfaee",
                    "on-surface": "#1b1c15",
                    "on-primary-fixed": "#131f00",
                    "on-tertiary-fixed": "#241a05",
                    "error-container": "#ffdad6",
                    "surface-container-high": "#eae8dd",
                    "on-tertiary-container": "#362a13",
                    "on-tertiary": "#ffffff",
                    "on-tertiary-fixed-variant": "#52452b",
                    "outline": "#76786b",
                    "on-secondary-fixed": "#351000",
                    "surface-variant": "#e5e3d7",
                    "on-surface-variant": "#46483c",
                    "on-primary-fixed-variant": "#3c4c1c",
                    "on-secondary-fixed-variant": "#6c391e",
                    "surface-bright": "#fcfaee",
                    "inverse-surface": "#303129",
                    "outline-variant": "#c6c8b8",
                    "surface-container-lowest": "#ffffff",
                    "tertiary": "#6b5c41",
                    "on-error-container": "#93000a",
                    "on-primary-container": "#223103"
            },
            "borderRadius": {
                    "DEFAULT": "1rem",
                    "lg": "2rem",
                    "xl": "3rem",
                    "full": "9999px"
            },
            "fontFamily": {
                    "headline": ["Noto Serif"],
                    "body": ["Plus Jakarta Sans"],
                    "label": ["Plus Jakarta Sans"]
            }
          },
        },
      }
    </script>
<style>
        .material-symbols-outlined {
            font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
        }
        .timeline-line {
            background: linear-gradient(to bottom, #d5ebaa 0%, #c6c8b8 100%);
        }
        body {
            font-family: 'Plus Jakarta Sans', sans-serif;
            background-color: #fcfaee;
            color: #1b1c15;
        }
        h1, h2, h3 {
            font-family: 'Noto Serif', serif;
        }
    </style>
</head>
<body class="bg-surface text-on-surface antialiased">
<!-- TopAppBar -->
<header class="flex justify-between items-center px-8 h-20 w-full sticky top-0 z-50 bg-[#fcfaee]/85 backdrop-blur-md">
<div class="flex items-center gap-4">
<span class="text-2xl font-bold font-['Noto_Serif'] text-[#536431]">Care Pulse</span>
</div>
<div class="hidden md:flex items-center gap-8">
<nav class="flex gap-6 items-center">
<a class="text-stone-500 hover:text-[#536431] transition-colors font-medium" href="#">Dashboard</a>
<a class="text-stone-500 hover:text-[#536431] transition-colors font-medium" href="#">Care Maze</a>
<a class="text-[#536431] font-bold" href="#">History</a>
</nav>
<div class="flex items-center gap-4 ml-4">
<button class="p-2 rounded-full hover:bg-[#f6f4e8] transition-colors">
<span class="material-symbols-outlined text-[#536431]">notifications</span>
</button>
<button class="p-2 rounded-full hover:bg-[#f6f4e8] transition-colors">
<span class="material-symbols-outlined text-[#536431]">favorite</span>
</button>
<div class="w-10 h-10 rounded-full overflow-hidden border-2 border-primary-fixed">
<img alt="User profile avatar" class="w-full h-full object-cover" data-alt="Portrait of a smiling woman with warm lighting and a soft natural background, professional yet approachable healthcare user" src="https://lh3.googleusercontent.com/aida-public/AB6AXuDIOAxx-Qvyxiy4YSYcO9riu4_y0cXwAbO8jjyNcotStmHoEm8xlUanYmmlhTBQnCEFBewXxbDW3csHxQo7sHUX4pr94P7PEAR73y6bP4pTTGKNtQSk7STfwQ_QDZn7HyzfBmIEVACwQ3f3aO9Y8tHX9poaxOCwoFKVb9JLrRTgz0xUcg1CCxEkuc8euRDiARzCPJdQMtCzlQrRvTOWaaNAc3ZdtEnlWFcCmNna1ojMZWo3LAtcUjZzvDnlWU8FLiyINXJDYElEqzdr"/>
</div>
</div>
</div>
</header>
<div class="flex min-h-[calc(100vh-5rem)]">
<!-- SideNavBar -->
<aside class="hidden md:flex flex-col h-full py-8 px-6 w-72 fixed left-0 top-20 bg-[#f6f4e8] border-r border-[#c6c8b8]/15 z-40">
<div class="mb-10">
<div class="flex items-center gap-3 mb-1">
<span class="material-symbols-outlined text-primary text-3xl">spa</span>
<h2 class="font-['Noto_Serif'] text-lg text-[#536431]">Nurturing Navigation</h2>
</div>
<p class="text-stone-500 text-xs font-medium ml-10">Your Digital Sanctuary</p>
</div>
<nav class="flex-1 space-y-2">
<a class="flex items-center gap-3 px-4 py-3 rounded-xl text-stone-600 opacity-80 hover:text-[#536431] hover:translate-x-1 transition-all font-medium" href="#">
<span class="material-symbols-outlined" data-icon="grid_view">grid_view</span>
                    Dashboard
                </a>
<a class="flex items-center gap-3 px-4 py-3 rounded-xl text-stone-600 opacity-80 hover:text-[#536431] hover:translate-x-1 transition-all font-medium" href="#">
<span class="material-symbols-outlined" data-icon="map">map</span>
                    Care Maze
                </a>
<a class="flex items-center gap-3 px-4 py-3 rounded-xl text-stone-600 opacity-80 hover:text-[#536431] hover:translate-x-1 transition-all font-medium" href="#">
<span class="material-symbols-outlined" data-icon="medication">medication</span>
                    Medications
                </a>
<a class="flex items-center gap-3 px-4 py-3 rounded-xl text-[#536431] font-bold border-r-4 border-[#536431]" href="#">
<span class="material-symbols-outlined" data-icon="history">history</span>
                    History
                </a>
</nav>
<div class="mt-auto space-y-2 pt-8">
<button class="w-full py-4 bg-gradient-to-br from-primary to-primary-container text-on-primary rounded-xl font-bold shadow-lg shadow-primary/10 mb-6 flex items-center justify-center gap-2">
<span class="material-symbols-outlined text-sm">support_agent</span>
                    Request Support
                </button>
<a class="flex items-center gap-3 px-4 py-2 text-stone-600 hover:text-primary transition-colors text-sm" href="#">
<span class="material-symbols-outlined text-xl" data-icon="settings">settings</span>
                    Settings
                </a>
<a class="flex items-center gap-3 px-4 py-2 text-stone-600 hover:text-primary transition-colors text-sm" href="#">
<span class="material-symbols-outlined text-xl" data-icon="help_outline">help_outline</span>
                    Help
                </a>
</div>
</aside>
<!-- Main Content Canvas -->
<main class="flex-1 md:ml-72 p-6 md:p-12 max-w-6xl mx-auto">
<!-- Header & Search -->
<div class="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-12">
<div class="space-y-2">
<h1 class="text-4xl md:text-5xl font-extrabold text-primary tracking-tight leading-tight">Clinical Context Timeline</h1>
<p class="text-stone-600 max-w-md text-lg leading-relaxed">A gentle look at your journey through care, curated to keep you informed and at ease.</p>
</div>
<div class="flex flex-col sm:flex-row gap-4 items-center">
<div class="relative w-full sm:w-64">
<span class="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-stone-400">search</span>
<input class="w-full pl-12 pr-4 py-3 bg-surface-container-high rounded-xl border-none focus:ring-4 focus:ring-primary-fixed/30 text-on-surface placeholder:text-stone-400" placeholder="Find specific notes" type="text"/>
</div>
<button class="whitespace-nowrap px-6 py-3 bg-secondary-container text-on-secondary-container rounded-xl font-bold flex items-center gap-2 hover:opacity-90 transition-opacity">
<span class="material-symbols-outlined">description</span>
                        Full Story
                    </button>
</div>
</div>
<!-- Timeline Section -->
<div class="relative">
<!-- Vertical Line -->
<div class="absolute left-6 md:left-8 top-4 bottom-4 w-1 timeline-line rounded-full opacity-30"></div>
<div class="space-y-12 relative">
<!-- Timeline Item 1 -->
<div class="flex gap-6 md:gap-10">
<div class="relative z-10 flex flex-col items-center">
<div class="w-12 h-12 md:w-16 md:h-16 rounded-full bg-primary-fixed flex items-center justify-center text-primary shadow-sm">
<span class="material-symbols-outlined text-2xl md:text-3xl" style="font-variation-settings: 'FILL' 1;">emergency</span>
</div>
</div>
<div class="flex-1 pt-2">
<div class="flex flex-col md:flex-row md:items-center justify-between mb-2 gap-1">
<span class="text-primary font-bold text-lg md:text-xl">St. Jude's ER</span>
<span class="text-stone-400 font-label text-sm font-medium">October 24, 2023 • 08:15 PM</span>
</div>
<div class="bg-surface-container-low p-6 md:p-8 rounded-lg md:rounded-xl relative overflow-hidden group">
<div class="absolute top-0 left-0 w-2 h-full bg-primary-container"></div>
<h3 class="font-headline text-lg text-primary mb-3">Plain Language Summary</h3>
<p class="text-on-surface text-lg leading-relaxed mb-6">
                                    They checked your blood pressure because of the dizzy spells you mentioned. Everything looked stable in the moment, but the doctor suggested a follow-up with your primary care provider within the next week to discuss a potential medication adjustment.
                                </p>
<div class="flex flex-wrap gap-3">
<span class="px-4 py-1.5 bg-white text-primary text-sm font-semibold rounded-full shadow-sm">Vital Check</span>
<span class="px-4 py-1.5 bg-white text-primary text-sm font-semibold rounded-full shadow-sm">Cardiology</span>
</div>
</div>
</div>
</div>
<!-- Timeline Item 2 -->
<div class="flex gap-6 md:gap-10">
<div class="relative z-10 flex flex-col items-center">
<div class="w-12 h-12 md:w-16 md:h-16 rounded-full bg-tertiary-fixed flex items-center justify-center text-tertiary shadow-sm">
<span class="material-symbols-outlined text-2xl md:text-3xl" style="font-variation-settings: 'FILL' 1;">medical_services</span>
</div>
</div>
<div class="flex-1 pt-2">
<div class="flex flex-col md:flex-row md:items-center justify-between mb-2 gap-1">
<span class="text-tertiary font-bold text-lg md:text-xl">City Health Diagnostics</span>
<span class="text-stone-400 font-label text-sm font-medium">October 18, 2023 • 10:30 AM</span>
</div>
<div class="bg-surface-container-high p-6 md:p-8 rounded-lg md:rounded-xl relative overflow-hidden">
<div class="absolute top-0 left-0 w-2 h-full bg-tertiary-container/30"></div>
<h3 class="font-headline text-lg text-tertiary mb-3">Plain Language Summary</h3>
<p class="text-on-surface text-lg leading-relaxed mb-6 italic">
                                    "Your annual blood work results came back. Your iron levels are a little low, which might explain why you've been feeling more tired than usual lately. We've added a gentle supplement to your care plan."
                                </p>
<div class="flex flex-wrap gap-3">
<span class="px-4 py-1.5 bg-white/50 text-tertiary text-sm font-semibold rounded-full border border-outline-variant/30">Lab Results</span>
<span class="px-4 py-1.5 bg-white/50 text-tertiary text-sm font-semibold rounded-full border border-outline-variant/30">Anemia Screen</span>
</div>
</div>
</div>
</div>
<!-- Nurture Card (Offset Inset) -->
<div class="ml-16 md:ml-24 py-4 pr-4">
<div class="bg-tertiary-container/10 p-8 rounded-lg flex flex-col md:flex-row items-center gap-8 border border-tertiary-container/20">
<div class="flex-1 space-y-4">
<h4 class="text-tertiary font-bold text-xl">Preparing for your next visit?</h4>
<p class="text-stone-600 leading-relaxed">
                                    We've noticed three mentions of fatigue across your last five visits. We can bundle these notes together into a 'Full Story' export to help your next doctor get the complete picture quickly.
                                </p>
<button class="text-primary font-bold flex items-center gap-2 group">
                                    Create visit summary
                                    <span class="material-symbols-outlined group-hover:translate-x-1 transition-transform">arrow_forward</span>
</button>
</div>
<div class="w-full md:w-48 h-32 rounded-2xl overflow-hidden shadow-inner">
<img alt="Stethoscope on a warm wooden table" class="w-full h-full object-cover" data-alt="Close-up of a stethoscope lying on a warm wooden table with soft morning sunlight filtering through a window" src="https://lh3.googleusercontent.com/aida-public/AB6AXuDY3lWqPZqeO5rVQ5YdkgRo9NWQ41RmD9h4QfW1K3h7aC8zc0v7Y93JwkOQNXxaa5HzzBbHHtmU-LwqRYetglXgFO0x5G2AkxW2WFrNZ4F0l0HOV0wYuJXDmpbTLT7MBaiHibWBAz9z6rmjOAsqKgGrkKPn5tMy-HTKl96sBJhoolhNv3vl5VDJBYAIhmeoFtuqmzOs3KPMzJyFThdAVkx73fK909k6MG-38w8l57iA0AtMHJpAcMO81pmuSIEfO_HJJgOW6Y7HdLwQ"/>
</div>
</div>
</div>
<!-- Timeline Item 3 -->
<div class="flex gap-6 md:gap-10">
<div class="relative z-10 flex flex-col items-center">
<div class="w-12 h-12 md:w-16 md:h-16 rounded-full bg-secondary-fixed flex items-center justify-center text-secondary shadow-sm">
<span class="material-symbols-outlined text-2xl md:text-3xl" style="font-variation-settings: 'FILL' 1;">pill</span>
</div>
</div>
<div class="flex-1 pt-2">
<div class="flex flex-col md:flex-row md:items-center justify-between mb-2 gap-1">
<span class="text-secondary font-bold text-lg md:text-xl">Riverside Pharmacy</span>
<span class="text-stone-400 font-label text-sm font-medium">October 12, 2023 • 04:45 PM</span>
</div>
<div class="bg-surface-container-low p-6 md:p-8 rounded-lg md:rounded-xl relative overflow-hidden">
<div class="absolute top-0 left-0 w-2 h-full bg-secondary-container"></div>
<h3 class="font-headline text-lg text-secondary mb-3">Plain Language Summary</h3>
<p class="text-on-surface text-lg leading-relaxed mb-6">
                                    Your refill for Lisinopril was picked up. The pharmacist noted that you should continue taking this in the morning with a full glass of water. They also reminded you to avoid grapefruit juice while on this medication.
                                </p>
<div class="flex flex-wrap gap-3">
<span class="px-4 py-1.5 bg-white text-secondary text-sm font-semibold rounded-full shadow-sm">Medication</span>
<span class="px-4 py-1.5 bg-white text-secondary text-sm font-semibold rounded-full shadow-sm">Refill</span>
</div>
</div>
</div>
</div>
<!-- End of Timeline Indicator -->
<div class="flex justify-center pt-8">
<button class="px-8 py-4 bg-surface-container-highest text-on-surface rounded-full font-bold hover:bg-surface-dim transition-colors">
                            Load Older Entries
                        </button>
</div>
</div>
</div>
</main>
</div>
<!-- Mobile Bottom Navigation -->
<nav class="md:hidden fixed bottom-0 left-0 right-0 h-16 bg-white/90 backdrop-blur-lg flex justify-around items-center px-4 z-50 shadow-[0_-4px_20px_rgba(0,0,0,0.05)]">
<button class="flex flex-col items-center gap-1 text-stone-400">
<span class="material-symbols-outlined">grid_view</span>
<span class="text-[10px] font-bold">Home</span>
</button>
<button class="flex flex-col items-center gap-1 text-stone-400">
<span class="material-symbols-outlined">map</span>
<span class="text-[10px] font-bold">Maze</span>
</button>
<button class="flex flex-col items-center gap-1 text-[#536431]">
<span class="material-symbols-outlined" style="font-variation-settings: 'FILL' 1;">history</span>
<span class="text-[10px] font-bold">History</span>
</button>
<button class="flex flex-col items-center gap-1 text-stone-400">
<span class="material-symbols-outlined">settings</span>
<span class="text-[10px] font-bold">Settings</span>
</button>
</nav>
</body></html>
all the code are four page layouts

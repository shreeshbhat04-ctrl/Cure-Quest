import { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { 
  Search, 
  ShieldAlert, 
  ShieldCheck, 
  ShieldQuestion, 
  Filter,
  TrendingUp,
  ShoppingCart,
  Check,
  X
} from 'lucide-react';
import { INGREDIENTS, Ingredient } from '../lib/ingredients';
import { Pill, SectionShell } from '../components/ui';

const STAGGER = {
  hidden: { opacity: 0, y: 20 },
  show: {
    opacity: 1,
    y: 0,
    transition: {
      staggerChildren: 0.1
    }
  }
};

const ITEM = {
  hidden: { opacity: 0, y: 10 },
  show: { opacity: 1, y: 0 }
};

interface MarketplaceScreenProps {
  onAddIngredient?: (name: string) => void;
  onClose?: () => void;
}

export function MarketplaceScreen({ onAddIngredient, onClose }: MarketplaceScreenProps = {}) {
  const [filter, setFilter] = useState<'All' | 'Fresh' | 'Pantry' | 'Protein' | 'Dairy'>('All');
  const [search, setSearch] = useState('');
  const [cartCount, setCartCount] = useState(0);

  const filteredIngredients = useMemo(() => {
    return INGREDIENTS.filter(item => {
      const matchesFilter = filter === 'All' || item.category === filter;
      const matchesSearch = item.name.toLowerCase().includes(search.toLowerCase());
      return matchesFilter && matchesSearch;
    });
  }, [filter, search]);

  const handleAddToCart = (item: Ingredient) => {
    if (item.status === 'Avoid') return;
    setCartCount(prev => prev + 1);
    if (onAddIngredient) {
      onAddIngredient(item.name.toLowerCase());
    }
  };

  return (
    <motion.div initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -18 }} className="space-y-8 pb-12">
      <div className="flex items-start justify-between">
        <SectionShell
          eyebrow="Marketplace"
          title={
            <>
              Rx Pantry: <span className="text-primary italic font-serif">Curated Ingredients</span>
            </>
          }
          description="Doctor-approved shopping list synchronized with your anti-inflammatory recovery protocol."
        />
        {onClose && (
          <button 
            onClick={onClose}
            className="rounded-full bg-surface-container-high p-2 text-on-surface hover:bg-surface-container-highest transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
        {/* Bento Stats Section */}
        <div className="md:col-span-12 grid grid-cols-1 md:grid-cols-12 gap-4">
          <div className="md:col-span-4 glass-panel p-8 flex items-center justify-between overflow-hidden relative group">
            <div className="absolute right-[-2rem] top-[-2rem] h-32 w-32 rounded-full bg-primary/10 blur-2xl group-hover:bg-primary/20 transition-all duration-500" />
            <div className="relative z-10">
              <p className="eyebrow text-primary/70 mb-2">Daily Target</p>
              <p className="font-serif text-3xl font-bold text-on-surface">2,200 <span className="text-sm font-sans font-medium text-on-surface/50">kcal</span></p>
            </div>
            <div className="w-px h-12 bg-outline-variant/30 mx-4"></div>
            <div className="relative z-10 text-right">
              <p className="eyebrow text-primary/70 mb-2">Protein Req.</p>
              <p className="font-serif text-3xl font-bold text-on-surface">125g</p>
            </div>
          </div>

          <div className="md:col-span-8 glass-panel p-8 flex items-center gap-6">
            <div className="h-14 w-14 rounded-2xl bg-primary-fixed/30 flex items-center justify-center shrink-0">
              <TrendingUp className="text-primary h-7 w-7" />
            </div>
            <div className="flex-1">
              <p className="eyebrow text-primary/70 mb-2">Compliance Insight</p>
              <p className="text-[1.05rem] leading-relaxed text-on-surface/80 font-serif">
                “Adding <span className="text-primary font-bold italic">Wild Salmon</span> fulfills your Omega-3 quota for the next 3 days per Dr. Aris's recommendation.”
              </p>
            </div>
          </div>
        </div>

        {/* Categories Sidebar */}
        <div className="md:col-span-3 lg:col-span-2 space-y-4">
          <div className="glass-panel p-3">
             <p className="eyebrow text-on-surface/40 px-3 py-2">Categories</p>
             <nav className="space-y-1">
              {(['All', 'Fresh', 'Protein', 'Pantry', 'Dairy'] as const).map((cat) => (
                <button
                  key={cat}
                  onClick={() => setFilter(cat)}
                  className={`w-full text-left px-4 py-3 rounded-xl text-sm font-medium transition-all ${
                    filter === cat 
                      ? 'bg-primary-fixed/30 text-primary' 
                      : 'text-on-surface/60 hover:bg-surface-container-lowest hover:text-primary'
                  }`}
                >
                  {cat === 'All' ? 'All Safe' : cat}
                </button>
              ))}
            </nav>
          </div>

          <div className="glass-panel p-6 bg-terracotta/5 border-terracotta/20">
            <p className="eyebrow text-terracotta/60 mb-2">Smart Alert</p>
            <p className="text-sm leading-6 text-on-surface/70">Avocados are 25% off today. Optimal for your healthy fats quota.</p>
          </div>
        </div>

        {/* Main Grid */}
        <div className="md:col-span-9 lg:col-span-10 space-y-6">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 px-2">
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-on-surface/30" />
              <input 
                type="text"
                placeholder="Search dr-approved ingredients..."
                className="w-full bg-surface-container-lowest/50 border border-outline-variant/30 rounded-2xl pl-11 pr-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary/20 transition-all"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
            <div className="flex items-center gap-4">
              <button className="flex items-center gap-2 text-[0.8rem] font-bold text-on-surface/40 uppercase tracking-widest hover:text-primary transition-colors">
                <Filter className="h-4 w-4" /> Sort: Compatibility
              </button>
            </div>
          </div>

          <motion.div 
            variants={STAGGER}
            initial="hidden"
            animate="show"
            className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6"
          >
            <AnimatePresence mode="popLayout">
              {filteredIngredients.map((item) => (
                <motion.div 
                  layout
                  key={item.id}
                  variants={ITEM}
                  initial="hidden"
                  animate="show"
                  exit={{ opacity: 0, scale: 0.9 }}
                  className="glass-panel group flex flex-col h-full relative"
                >
                  {/* Safety Watermark */}
                  <div className="absolute top-4 right-4 z-10">
                    {item.status === 'Safe' && (
                      <div className="p-1.5 bg-primary-fixed/40 rounded-lg text-primary glass-edge">
                        <ShieldCheck className="w-4 h-4" />
                      </div>
                    )}
                    {item.status === 'Watch' && (
                      <div className="p-1.5 bg-tertiary-container/30 rounded-lg text-tertiary glass-edge">
                        <ShieldQuestion className="w-4 h-4" />
                      </div>
                    )}
                    {item.status === 'Avoid' && (
                      <div className="p-1.5 bg-terracotta/10 rounded-lg text-terracotta glass-edge">
                        <ShieldAlert className="w-4 h-4" />
                      </div>
                    )}
                  </div>

                  <div className="aspect-[4/3] rounded-xl mb-5 overflow-hidden bg-surface-container-low/50">
                    <img 
                      src={item.image} 
                      alt={item.name}
                      className={`w-full h-full object-cover group-hover:scale-105 transition-transform duration-500 ${item.status === 'Avoid' ? 'grayscale opacity-60' : ''}`}
                    />
                  </div>
                  
                  <div className="flex flex-col flex-1">
                    <div className="flex justify-between items-start mb-2">
                      <h4 className="font-serif font-bold text-[1.1rem] text-on-surface leading-tight">{item.name}</h4>
                      <span className="font-serif text-[0.95rem] font-bold text-primary">${item.price.toFixed(2)}</span>
                    </div>
                    <p className="eyebrow text-on-surface/30 mb-4">{item.category}</p>
                    
                    <div className={`mt-auto p-4 rounded-xl text-[0.85rem] leading-6 glass-edge ${
                      item.status === 'Safe' ? 'bg-primary-fixed/10 text-primary/80' :
                      item.status === 'Watch' ? 'bg-tertiary-container/10 text-tertiary/80' :
                      'bg-terracotta/5 text-terracotta/80'
                    }`}>
                      <p className="font-bold flex items-center gap-2 mb-1">
                         {item.status === 'Safe' ? 'Recommended' : item.status === 'Watch' ? 'Monitor Intake' : 'Non-Compliant'}
                      </p>
                      <p className="opacity-80 font-sans">{item.reason}</p>
                    </div>

                    <button 
                      onClick={() => handleAddToCart(item)}
                      className={`w-full mt-5 py-3 rounded-xl text-[0.85rem] font-bold tracking-widest uppercase transition-all ${
                        item.status === 'Avoid' 
                        ? 'bg-surface-container-high/40 text-on-surface/20 cursor-not-allowed glass-edge' 
                        : 'bg-on-surface text-surface hover:bg-primary hover:text-white shadow-sm'
                      }`}
                    >
                      {item.status === 'Avoid' ? 'Restricted' : 'Add to Pantry'}
                    </button>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </motion.div>
        </div>
      </div>
    </motion.div>
  );
}

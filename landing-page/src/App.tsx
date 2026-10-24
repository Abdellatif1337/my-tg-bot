import { useMemo, useState } from 'react'
import type { LucideIcon } from 'lucide-react'
import {
  BatteryMedium,
  Briefcase,
  CheckCircle2,
  ChevronDown,
  CircleDollarSign,
  Code2,
  Cpu,
  GraduationCap,
  HardDrive,
  Headphones,
  Laptop,
  Menu,
  MessageCircle,
  Monitor,
  ShieldCheck,
  Sparkles,
  Users,
  X,
} from 'lucide-react'

type SpecItem = {
  label: string
  value: string
  icon: LucideIcon
}

type ConditionItem = {
  label: string
  value: string
}

type FaqItem = {
  question: string
  answer: string
}

const productData = {
  storeName: 'EliteBook Store',
  productName: 'HP EliteBook',
  model: 'Modèle à renseigner',
  price: 'À renseigner',
  currency: 'DH',
  originalPrice: '',
  phoneNumber: '212XXXXXXXXX',
  instagramUrl: 'https://instagram.com/votre_compte',
  supportInfo: 'Support client: 7j/7 (horaires à renseigner)',
  deliveryOptions: 'Livraison locale et nationale à renseigner',
  reassurance: 'Contactez-nous sur WhatsApp pour confirmer la disponibilité avant commande.',
  heroTitle: 'La performance professionnelle, à votre portée.',
  heroText:
    'Un ordinateur pensé pour la productivité, la mobilité et un usage professionnel quotidien. Informations techniques ci-dessous à compléter selon votre modèle exact.',
  images: [
    {
      src: 'https://placehold.co/1200x800/f3f4f6/111827?text=Photo+réelle+HP+EliteBook+à+ajouter',
      alt: 'Placeholder photo principale HP EliteBook à remplacer par une photo réelle du modèle.',
    },
    {
      src: 'https://placehold.co/1200x800/e5e7eb/111827?text=Vue+clavier+à+ajouter',
      alt: 'Placeholder vue clavier HP EliteBook à remplacer.',
    },
    {
      src: 'https://placehold.co/1200x800/e2e8f0/111827?text=Vue+profil+à+ajouter',
      alt: 'Placeholder vue profil HP EliteBook à remplacer.',
    },
    {
      src: 'https://placehold.co/1200x800/edf2f7/111827?text=Vue+ports+à+ajouter',
      alt: 'Placeholder vue des ports HP EliteBook à remplacer.',
    },
  ],
}

const specs: SpecItem[] = [
  { label: 'Processeur', value: 'À renseigner', icon: Cpu },
  { label: 'RAM', value: 'À renseigner', icon: Laptop },
  { label: 'Stockage SSD', value: 'À renseigner', icon: HardDrive },
  { label: 'Taille d’écran', value: 'À renseigner', icon: Monitor },
  { label: 'Graphiques', value: 'À renseigner', icon: Sparkles },
  { label: 'État batterie', value: 'À renseigner', icon: BatteryMedium },
  { label: 'État esthétique', value: 'À renseigner', icon: CheckCircle2 },
  { label: 'Système', value: 'À renseigner', icon: ShieldCheck },
]

const conditionDetails: ConditionItem[] = [
  { label: 'État du produit', value: 'Neuf / Occasion (à sélectionner)' },
  { label: 'Batterie', value: 'Capacité/état réel à renseigner' },
  { label: 'État cosmétique', value: 'Rayures, usure, défauts éventuels à préciser' },
  { label: 'Garantie', value: 'À renseigner (si applicable)' },
  { label: 'Accessoires inclus', value: 'Chargeur, sac, etc. à renseigner' },
  { label: 'Livraison', value: productData.deliveryOptions },
]

const benefitCards = [
  {
    title: 'Étudiants',
    text: 'Format pratique pour les cours, recherches et travaux académiques selon la configuration indiquée.',
    icon: GraduationCap,
  },
  {
    title: 'Programmeurs',
    text: 'Confort de travail pour les environnements de développement compatibles avec les caractéristiques affichées.',
    icon: Code2,
  },
  {
    title: 'Employés de bureau',
    text: 'Idéal pour bureautique, visioconférence et outils collaboratifs selon les spécifications du modèle.',
    icon: Briefcase,
  },
  {
    title: 'Professionnels',
    text: 'Design sobre et usage professionnel avec transparence totale sur l’état et les composants.',
    icon: Users,
  },
]

const faqs: FaqItem[] = [
  { question: 'Le laptop est-il disponible ?', answer: 'Disponibilité à confirmer en temps réel via WhatsApp.' },
  {
    question: 'Puis-je vérifier le laptop avant achat ?',
    answer: 'Oui, modalités de vérification à renseigner selon votre ville.',
  },
  {
    question: 'La livraison est-elle possible ?',
    answer: 'Oui, options et délais de livraison à renseigner.',
  },
  {
    question: 'Quel est l’état de la batterie ?',
    answer: 'État réel de la batterie à renseigner dans la section transparence.',
  },
  { question: 'Y a-t-il une garantie ?', answer: 'Garantie à renseigner si applicable.' },
  {
    question: 'Comment commander ?',
    answer: 'Cliquez sur “Commander sur WhatsApp” pour discuter directement avec le vendeur.',
  },
]

const currentYear = new Date().getFullYear()

function App() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const [selectedImage, setSelectedImage] = useState(0)
  const [openFaq, setOpenFaq] = useState<number | null>(0)

  const whatsappUrl = useMemo(() => {
    const message = `Bonjour, je suis intéressé(e) par ${productData.productName}.\nModèle: ${productData.model}\nPrix affiché: ${productData.price} ${productData.currency}\nLe produit est-il toujours disponible ?`
    return `https://wa.me/${productData.phoneNumber}?text=${encodeURIComponent(message)}`
  }, [])

  return (
    <div className="page">
      <header className="topbar" id="home">
        <a className="logo" href="#home">
          {productData.storeName}
        </a>
        <button
          type="button"
          className="menu-toggle"
          onClick={() => setIsMenuOpen((value) => !value)}
          aria-expanded={isMenuOpen}
          aria-controls="main-navigation"
          aria-label="Ouvrir le menu"
        >
          {isMenuOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
        <nav id="main-navigation" className={`nav ${isMenuOpen ? 'open' : ''}`} aria-label="Navigation principale">
          <a href="#home" onClick={() => setIsMenuOpen(false)}>
            Home
          </a>
          <a href="#specifications" onClick={() => setIsMenuOpen(false)}>
            Specifications
          </a>
          <a href="#benefits" onClick={() => setIsMenuOpen(false)}>
            Benefits
          </a>
          <a href="#faq" onClick={() => setIsMenuOpen(false)}>
            FAQ
          </a>
          <a className="button button-small" href={whatsappUrl} target="_blank" rel="noreferrer">
            Commander sur WhatsApp
          </a>
        </nav>
      </header>

      <main>
        <section className="hero section">
          <div className="hero-content">
            <p className="kicker">HP EliteBook • Maroc</p>
            <h1>{productData.heroTitle}</h1>
            <p>{productData.heroText}</p>
            <div className="hero-meta">
              <p className="model">Modèle: {productData.model}</p>
              <p className="price">
                {productData.price} <span>{productData.currency}</span>
              </p>
            </div>
            <div className="cta-group">
              <a className="button" href={whatsappUrl} target="_blank" rel="noreferrer">
                Commander maintenant
              </a>
              <a className="button button-ghost" href="#specifications">
                Voir les caractéristiques
              </a>
            </div>
            <ul className="trust-list" aria-label="Éléments de confiance">
              <li>
                <CircleDollarSign size={16} /> Prix transparent
              </li>
              <li>
                <MessageCircle size={16} /> Contact direct
              </li>
              <li>
                <Headphones size={16} /> Assistance client
              </li>
            </ul>
          </div>
          <figure className="hero-image-card">
            <img src={productData.images[selectedImage].src} alt={productData.images[selectedImage].alt} loading="eager" />
            <figcaption>Photo à remplacer par l’image réelle du modèle vendu.</figcaption>
          </figure>
        </section>

        <section className="section" aria-labelledby="gallery-title">
          <div className="section-head">
            <h2 id="gallery-title">Galerie produit</h2>
            <p>Utilisez des photos réelles et récentes du laptop proposé.</p>
          </div>
          <div className="gallery-layout">
            <img
              className="gallery-main"
              src={productData.images[selectedImage].src}
              alt={productData.images[selectedImage].alt}
              loading="lazy"
            />
            <div className="thumbs" role="list" aria-label="Miniatures du produit">
              {productData.images.map((image, index) => (
                <button
                  type="button"
                  key={image.src}
                  className={`thumb ${selectedImage === index ? 'active' : ''}`}
                  onClick={() => setSelectedImage(index)}
                  aria-label={`Voir image ${index + 1}`}
                >
                  <img src={image.src} alt={image.alt} loading="lazy" />
                </button>
              ))}
            </div>
          </div>
        </section>

        <section className="section" id="specifications" aria-labelledby="spec-title">
          <div className="section-head">
            <h2 id="spec-title">Caractéristiques techniques</h2>
            <p>Les champs ci-dessous sont éditables et doivent refléter le modèle exact.</p>
          </div>
          <div className="spec-grid">
            {specs.map((item) => (
              <article className="spec-card" key={item.label}>
                <item.icon size={20} aria-hidden="true" />
                <h3>{item.label}</h3>
                <p>{item.value}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="section" id="benefits" aria-labelledby="benefits-title">
          <div className="section-head">
            <h2 id="benefits-title">Pourquoi choisir ce laptop ?</h2>
            <p>Des bénéfices concrets selon l’usage réel et la configuration fournie.</p>
          </div>
          <div className="benefits-grid">
            {benefitCards.map((item) => (
              <article key={item.title} className="benefit-card">
                <item.icon size={20} aria-hidden="true" />
                <h3>{item.title}</h3>
                <p>{item.text}</p>
              </article>
            ))}
          </div>
          <a className="button section-cta" href={whatsappUrl} target="_blank" rel="noreferrer">
            Commander sur WhatsApp
          </a>
        </section>

        <section className="section" aria-labelledby="transparency-title">
          <div className="section-head">
            <h2 id="transparency-title">État du produit & transparence</h2>
            <p>Toutes les informations importantes sont visibles avant contact.</p>
          </div>
          <div className="condition-list" role="list">
            {conditionDetails.map((item) => (
              <div key={item.label} className="condition-item" role="listitem">
                <p>{item.label}</p>
                <strong>{item.value}</strong>
              </div>
            ))}
          </div>
        </section>

        <section className="section pricing" aria-labelledby="pricing-title">
          <div>
            <h2 id="pricing-title">Prix et commande</h2>
            <p>{productData.reassurance}</p>
          </div>
          <div className="pricing-card">
            {productData.originalPrice ? <p className="old-price">{productData.originalPrice}</p> : null}
            <p className="current-price">
              {productData.price} {productData.currency}
            </p>
            <a className="button" href={whatsappUrl} target="_blank" rel="noreferrer">
              Commander maintenant
            </a>
            <small>Réponse rapide sur WhatsApp pour disponibilité et détails de livraison.</small>
          </div>
        </section>

        <section className="section" id="faq" aria-labelledby="faq-title">
          <div className="section-head">
            <h2 id="faq-title">FAQ</h2>
            <p>Questions fréquentes avant achat.</p>
          </div>
          <div className="faq-list">
            {faqs.map((item, index) => {
              const isOpen = openFaq === index
              return (
                <article key={item.question} className="faq-item">
                  <button
                    type="button"
                    className="faq-question"
                    aria-expanded={isOpen}
                    onClick={() => setOpenFaq(isOpen ? null : index)}
                  >
                    <span>{item.question}</span>
                    <ChevronDown size={18} className={isOpen ? 'rotate' : ''} aria-hidden="true" />
                  </button>
                  {isOpen ? <p className="faq-answer">{item.answer}</p> : null}
                </article>
              )
            })}
          </div>
        </section>
      </main>

      <footer className="footer">
        <div>
          <p className="logo">{productData.storeName}</p>
          <p>WhatsApp: {productData.phoneNumber}</p>
        </div>
        <div>
          <a href={productData.instagramUrl} target="_blank" rel="noreferrer">
            Instagram
          </a>
          <p>{productData.supportInfo}</p>
        </div>
        <p>© {currentYear} {productData.storeName}. Tous droits réservés.</p>
      </footer>

      <aside className="sticky-buy" aria-label="Commande rapide mobile">
        <div>
          <p>{productData.productName}</p>
          <strong>
            {productData.price} {productData.currency}
          </strong>
        </div>
        <a className="button button-small" href={whatsappUrl} target="_blank" rel="noreferrer">
          Commander
        </a>
      </aside>
    </div>
  )
}

export default App

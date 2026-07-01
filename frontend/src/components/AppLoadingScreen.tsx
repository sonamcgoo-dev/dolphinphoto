import { motion } from 'framer-motion'
import logoImage from '@/assets/dolphinphoto-logo.png'
import dolphinLaughImage from '@/assets/dolphin-laugh.png'

export default function AppLoadingScreen() {
  return (
    <div className="min-h-screen bg-space-900 flex items-center justify-center p-6">
      <div className="text-center">
        <img
          src={logoImage}
          alt="DolphinPhoto"
          className="h-16 w-auto mx-auto mb-5 object-contain"
        />
        <motion.img
          src={dolphinLaughImage}
          alt="Laughing dolphin loading"
          className="w-48 h-48 object-cover rounded-2xl shadow-lg shadow-accent-magenta/30 mx-auto"
          animate={{
            y: [0, -8, 2, -6, 0],
            rotate: [0, -1.2, 1.2, -1, 0],
            scale: [1, 1.02, 1.01, 1.03, 1],
          }}
          transition={{
            duration: 1.1,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />
        <motion.p
          className="mt-5 text-sm tracking-[0.18em] uppercase text-accent-cyan"
          animate={{ opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 1.1, repeat: Infinity }}
        >
          Loading DolphinPhoto...
        </motion.p>
      </div>
    </div>
  )
}

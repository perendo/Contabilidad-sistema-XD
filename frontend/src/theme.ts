import { createTheme } from '@mui/material/styles'
import { esES } from '@mui/material/locale'

export const tema = createTheme(
  {
    palette: {
      primary: { main: '#1565c0' },
      background: { default: '#f5f7fa' },
    },
    shape: { borderRadius: 8 },
  },
  esES,
)

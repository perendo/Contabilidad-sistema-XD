import { useState } from 'react'
import type { FormEvent } from 'react'
import Alert from '@mui/material/Alert'
import Box from '@mui/material/Box'
import Button from '@mui/material/Button'
import CircularProgress from '@mui/material/CircularProgress'
import Paper from '@mui/material/Paper'
import Stack from '@mui/material/Stack'
import TextField from '@mui/material/TextField'
import Typography from '@mui/material/Typography'
import axios from 'axios'
import { Navigate, useNavigate } from 'react-router-dom'
import { useSesion } from '../sesion.tsx'

function LoginPage() {
  const { usuario, cargando, aviso, iniciarSesion } = useSesion()
  const navegar = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [enviando, setEnviando] = useState(false)

  if (cargando) {
    return (
      <Box sx={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <CircularProgress />
      </Box>
    )
  }

  if (usuario) {
    return <Navigate to="/entidades" replace />
  }

  const entrar = async (evento: FormEvent) => {
    evento.preventDefault()
    setError('')
    setEnviando(true)
    try {
      await iniciarSesion(email, password)
      navegar('/entidades', { replace: true })
    } catch (fallo) {
      const detalle = axios.isAxiosError(fallo) ? fallo.response?.data?.detail : undefined
      setError(typeof detalle === 'string' ? detalle : 'No se pudo iniciar sesión')
    } finally {
      setEnviando(false)
    }
  }

  return (
    <Box sx={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', p: 2 }}>
      <Paper component="section" elevation={2} sx={{ p: 4, width: '100%', maxWidth: 420 }}>
        <Typography variant="h5" component="h1" gutterBottom>
          Sistema Contable ONG
        </Typography>
        <Typography color="text.secondary" sx={{ mb: 3 }}>
          Entra con tu email y tu contraseña.
        </Typography>
        <Stack component="form" spacing={2} onSubmit={entrar}>
          <TextField
            label="Email"
            type="email"
            value={email}
            onChange={(evento) => setEmail(evento.target.value)}
            autoComplete="email"
            required
            fullWidth
          />
          <TextField
            label="Contraseña"
            type="password"
            value={password}
            onChange={(evento) => setPassword(evento.target.value)}
            autoComplete="current-password"
            required
            fullWidth
          />
          {error && <Alert severity="error">{error}</Alert>}
          {!error && aviso && <Alert severity="info">{aviso}</Alert>}
          <Button type="submit" variant="contained" size="large" disabled={enviando}>
            {enviando ? 'Entrando…' : 'Entrar'}
          </Button>
        </Stack>
      </Paper>
    </Box>
  )
}

export default LoginPage

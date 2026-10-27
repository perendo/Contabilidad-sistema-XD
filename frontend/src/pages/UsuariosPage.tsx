import { useCallback, useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import Alert from '@mui/material/Alert'
import Button from '@mui/material/Button'
import MenuItem from '@mui/material/MenuItem'
import Paper from '@mui/material/Paper'
import Stack from '@mui/material/Stack'
import Table from '@mui/material/Table'
import TableBody from '@mui/material/TableBody'
import TableCell from '@mui/material/TableCell'
import TableContainer from '@mui/material/TableContainer'
import TableHead from '@mui/material/TableHead'
import TableRow from '@mui/material/TableRow'
import TextField from '@mui/material/TextField'
import Typography from '@mui/material/Typography'
import axios from 'axios'
import { cliente } from '../api/cliente.ts'
import { NOMBRES_ROL } from '../sesion.tsx'

type Rol = {
  id: string
  nombre: 'administrador' | 'tesorero' | 'solo_lectura'
  descripcion: string | null
}

type Usuario = {
  id: string
  email: string
  nombre_completo: string
  activo: boolean
  creado_en: string
  rol: Rol
}

function UsuariosPage() {
  const [usuarios, setUsuarios] = useState<Usuario[]>([])
  const [roles, setRoles] = useState<Rol[]>([])
  const [nombreCompleto, setNombreCompleto] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [rolId, setRolId] = useState('')
  const [error, setError] = useState('')

  const cargar = useCallback(async () => {
    const [{ data: usuariosData }, { data: rolesData }] = await Promise.all([
      cliente.get<Usuario[]>('/usuarios'),
      cliente.get<Rol[]>('/usuarios/roles'),
    ])
    setUsuarios(usuariosData)
    setRoles(rolesData)
    if (!rolId && rolesData.length > 0) {
      setRolId(rolesData[0].id)
    }
  }, [rolId])

  useEffect(() => {
    cargar().catch(() => setError('No se pudo cargar el listado de usuarios'))
  }, [cargar])

  const crear = async (evento: FormEvent) => {
    evento.preventDefault()
    setError('')
    try {
      await cliente.post('/usuarios', {
        nombre_completo: nombreCompleto,
        email,
        password,
        rol_id: rolId,
      })
      setNombreCompleto('')
      setEmail('')
      setPassword('')
      await cargar()
    } catch (fallo) {
      const detalle = axios.isAxiosError(fallo) ? fallo.response?.data?.detail : undefined
      setError(typeof detalle === 'string' ? detalle : 'No se pudo dar de alta el usuario')
    }
  }

  return (
    <Stack spacing={4}>
      <Paper component="section" elevation={1} sx={{ p: 3 }}>
        <Typography variant="h5" component="h2" gutterBottom>
          Alta de usuario
        </Typography>
        <Stack component="form" spacing={2} onSubmit={crear}>
          <TextField
            label="Nombre completo"
            value={nombreCompleto}
            onChange={(evento) => setNombreCompleto(evento.target.value)}
            required
            fullWidth
          />
          <TextField
            label="Email"
            type="email"
            value={email}
            onChange={(evento) => setEmail(evento.target.value)}
            required
            fullWidth
          />
          <TextField
            label="Contraseña inicial"
            type="password"
            value={password}
            onChange={(evento) => setPassword(evento.target.value)}
            required
            fullWidth
          />
          <TextField
            label="Rol"
            select
            value={rolId}
            onChange={(evento) => setRolId(evento.target.value)}
            required
            fullWidth
          >
            {roles.map((rol) => (
              <MenuItem key={rol.id} value={rol.id}>
                {NOMBRES_ROL[rol.nombre]}
              </MenuItem>
            ))}
          </TextField>
          {error && <Alert severity="error">{error}</Alert>}
          <Button type="submit" variant="contained">
            Dar de alta
          </Button>
        </Stack>
      </Paper>

      <Paper component="section" elevation={1} sx={{ p: 3 }}>
        <Typography variant="h5" component="h2" gutterBottom>
          Usuarios
        </Typography>
        {usuarios.length === 0 ? (
          <Typography color="text.secondary">Todavía no hay usuarios.</Typography>
        ) : (
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Nombre</TableCell>
                  <TableCell>Email</TableCell>
                  <TableCell>Rol</TableCell>
                  <TableCell>Activo</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {usuarios.map((usuario) => (
                  <TableRow key={usuario.id}>
                    <TableCell>{usuario.nombre_completo}</TableCell>
                    <TableCell>{usuario.email}</TableCell>
                    <TableCell>{NOMBRES_ROL[usuario.rol.nombre]}</TableCell>
                    <TableCell>{usuario.activo ? 'Sí' : 'No'}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Paper>
    </Stack>
  )
}

export default UsuariosPage

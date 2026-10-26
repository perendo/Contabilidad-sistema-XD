import { useCallback, useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import Alert from '@mui/material/Alert'
import Button from '@mui/material/Button'
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

type Ejercicio = {
  id: string
  anio: number
  fecha_inicio: string
  fecha_fin: string
  cerrado: boolean
}

type Entidad = {
  id: string
  cif: string
  nombre: string
  activa: boolean
  creada_en: string
  ejercicios: Ejercicio[]
}

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api/v1'

function EntidadesPage() {
  const [entidades, setEntidades] = useState<Entidad[]>([])
  const [cif, setCif] = useState('')
  const [nombre, setNombre] = useState('')
  const [anio, setAnio] = useState(String(new Date().getFullYear()))
  const [error, setError] = useState('')

  const cargar = useCallback(async () => {
    const { data } = await axios.get<Entidad[]>(`${API_URL}/entidades`)
    setEntidades(data)
  }, [])

  useEffect(() => {
    cargar().catch(() => setError('No se pudo cargar el listado de entidades'))
  }, [cargar])

  const crear = async (evento: FormEvent) => {
    evento.preventDefault()
    setError('')
    try {
      await axios.post(`${API_URL}/entidades`, { cif, nombre, anio: Number(anio) })
      setCif('')
      setNombre('')
      await cargar()
    } catch (fallo) {
      const detalle = axios.isAxiosError(fallo) ? fallo.response?.data?.detail : undefined
      setError(typeof detalle === 'string' ? detalle : 'No se pudo dar de alta la entidad')
    }
  }

  return (
    <Stack spacing={4}>
      <Paper component="section" elevation={1} sx={{ p: 3 }}>
        <Typography variant="h5" component="h2" gutterBottom>
          Alta de entidad
        </Typography>
        <Stack component="form" spacing={2} onSubmit={crear}>
          <TextField
            label="CIF"
            value={cif}
            onChange={(evento) => setCif(evento.target.value)}
            required
            fullWidth
          />
          <TextField
            label="Nombre"
            value={nombre}
            onChange={(evento) => setNombre(evento.target.value)}
            required
            fullWidth
          />
          <TextField
            label="Ejercicio contable"
            type="number"
            value={anio}
            onChange={(evento) => setAnio(evento.target.value)}
            helperText="Se creará del 1 de enero al 31 de diciembre de ese año"
            required
            fullWidth
          />
          {error && <Alert severity="error">{error}</Alert>}
          <Button type="submit" variant="contained">
            Dar de alta
          </Button>
        </Stack>
      </Paper>

      <Paper component="section" elevation={1} sx={{ p: 3 }}>
        <Typography variant="h5" component="h2" gutterBottom>
          Entidades
        </Typography>
        {entidades.length === 0 ? (
          <Typography color="text.secondary">Todavía no hay entidades.</Typography>
        ) : (
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>CIF</TableCell>
                  <TableCell>Nombre</TableCell>
                  <TableCell>Ejercicio</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {entidades.map((entidad) => (
                  <TableRow key={entidad.id}>
                    <TableCell>{entidad.cif}</TableCell>
                    <TableCell>{entidad.nombre}</TableCell>
                    <TableCell>{entidad.ejercicios.map((ejercicio) => ejercicio.anio).join(', ')}</TableCell>
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

export default EntidadesPage

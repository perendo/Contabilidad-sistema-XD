import { useCallback, useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import AddIcon from '@mui/icons-material/Add'
import DeleteIcon from '@mui/icons-material/Delete'
import Alert from '@mui/material/Alert'
import Button from '@mui/material/Button'
import IconButton from '@mui/material/IconButton'
import MenuItem from '@mui/material/MenuItem'
import Paper from '@mui/material/Paper'
import Select from '@mui/material/Select'
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
import { useSesion } from '../sesion.tsx'

type Cuenta = {
  id: string
  codigo: string
  nombre: string
  grupo: string
  activa: boolean
}

type Apunte = {
  id: string
  cuenta_id: string
  tipo: 'debe' | 'haber'
  importe: string
}

type Asiento = {
  id: string
  entidad_id: string
  ejercicio_id: string
  numero_asiento: number
  fecha: string
  concepto: string
  descripcion: string | null
  registrado_por_id: string
  creado_en: string
  modificado_en: string
  apuntes: Apunte[]
}

type ApunteFormulario = {
  cuenta_id: string
  tipo: 'debe' | 'haber'
  importe: string
}

function AsientosPage() {
  const { entidadSeleccionadaId, ejercicioSeleccionadoId, entidadSeleccionada, ejercicioSeleccionado, usuario } = useSesion()
  const [cuentas, setCuentas] = useState<Cuenta[]>([])
  const [asientos, setAsientos] = useState<Asiento[]>([])
  const [fecha, setFecha] = useState(new Date().toISOString().slice(0, 10))
  const [concepto, setConcepto] = useState('')
  const [descripcion, setDescripcion] = useState('')
  const [apuntes, setApuntes] = useState<ApunteFormulario[]>([
    { cuenta_id: '', tipo: 'debe', importe: '' },
    { cuenta_id: '', tipo: 'haber', importe: '' },
  ])
  const [error, setError] = useState('')
  const [guardando, setGuardando] = useState(false)

  const cargarCuentas = useCallback(async () => {
    if (!entidadSeleccionadaId) return
    const { data } = await cliente.get<Cuenta[]>('/cuentas', { params: { entidad_id: entidadSeleccionadaId } })
    setCuentas(data)
  }, [entidadSeleccionadaId])

  const cargarAsientos = useCallback(async () => {
    if (!entidadSeleccionadaId || !ejercicioSeleccionadoId) return
    const { data } = await cliente.get<Asiento[]>('/asientos', {
      params: { entidad_id: entidadSeleccionadaId, ejercicio_id: ejercicioSeleccionadoId },
    })
    setAsientos(data)
  }, [entidadSeleccionadaId, ejercicioSeleccionadoId])

  useEffect(() => {
    cargarCuentas().catch(() => undefined)
  }, [cargarCuentas])

  useEffect(() => {
    cargarAsientos().catch(() => setError('No se pudo cargar el listado de asientos'))
  }, [cargarAsientos])

  const puedeCrear = usuario?.rol.nombre === 'administrador' || usuario?.rol.nombre === 'tesorero'

  const actualizarApunte = (indice: number, campo: keyof ApunteFormulario, valor: string) => {
    setApuntes((actuales) => {
      const copia = [...actuales]
      copia[indice] = { ...copia[indice], [campo]: valor }
      return copia
    })
  }

  const anadirApunte = () => {
    setApuntes((actuales) => [...actuales, { cuenta_id: '', tipo: 'debe', importe: '' }])
  }

  const eliminarApunte = (indice: number) => {
    if (apuntes.length <= 2) return
    setApuntes((actuales) => actuales.filter((_, i) => i !== indice))
  }

  const crear = async (evento: FormEvent) => {
    evento.preventDefault()
    if (!entidadSeleccionadaId || !ejercicioSeleccionadoId) {
      setError('Selecciona una entidad y un ejercicio en la cabecera.')
      return
    }
    setError('')
    setGuardando(true)
    try {
      const payload = {
        entidad_id: entidadSeleccionadaId,
        ejercicio_id: ejercicioSeleccionadoId,
        fecha,
        concepto,
        descripcion: descripcion || undefined,
        apuntes: apuntes
          .filter((a) => a.cuenta_id && a.importe)
          .map((a) => ({ cuenta_id: a.cuenta_id, tipo: a.tipo, importe: a.importe })),
      }
      await cliente.post('/asientos', payload)
      setConcepto('')
      setDescripcion('')
      setApuntes([
        { cuenta_id: '', tipo: 'debe', importe: '' },
        { cuenta_id: '', tipo: 'haber', importe: '' },
      ])
      await cargarAsientos()
    } catch (fallo) {
      const detalle = axios.isAxiosError(fallo) ? fallo.response?.data?.detail : undefined
      if (typeof detalle === 'string') {
        setError(detalle)
      } else if (Array.isArray(detalle)) {
        setError(detalle.map((d: any) => d.msg).join(', '))
      } else {
        setError('No se pudo crear el asiento')
      }
    } finally {
      setGuardando(false)
    }
  }

  if (!entidadSeleccionadaId || !ejercicioSeleccionadoId) {
    return (
      <Alert severity="info">
        Selecciona una entidad y un ejercicio en la cabecera para habilitar el diario de asientos.
      </Alert>
    )
  }

  return (
    <Stack spacing={4}>
      {puedeCrear && (
        <Paper component="section" elevation={1} sx={{ p: 3 }}>
          <Typography variant="h5" component="h2" gutterBottom>
            Nuevo asiento
          </Typography>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            {entidadSeleccionada?.nombre} · Ejercicio {ejercicioSeleccionado?.anio}
          </Typography>
          <Stack component="form" spacing={2} onSubmit={crear}>
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
              <TextField label="Fecha" type="date" value={fecha} onChange={(e) => setFecha(e.target.value)} required sx={{ flex: 1 }} slotProps={{ inputLabel: { shrink: true } }} />
              <TextField label="Concepto" value={concepto} onChange={(e) => setConcepto(e.target.value)} required sx={{ flex: 2 }} />
            </Stack>
            <TextField label="Descripción" value={descripcion} onChange={(e) => setDescripcion(e.target.value)} fullWidth />
            <Typography variant="subtitle1">Apuntes (debe / haber)</Typography>
            <Stack spacing={1}>
              {apuntes.map((apunte, indice) => (
                <Stack key={indice} direction={{ xs: 'column', sm: 'row' }} spacing={1} sx={{ alignItems: { sm: 'center' } }}>
                  <Select value={apunte.cuenta_id} onChange={(e) => actualizarApunte(indice, 'cuenta_id', e.target.value)} displayEmpty sx={{ flex: 2, minWidth: 200 }}>
                    <MenuItem value="" disabled>
                      Selecciona cuenta
                    </MenuItem>
                    {cuentas.map((cuenta) => (
                      <MenuItem key={cuenta.id} value={cuenta.id}>
                        {cuenta.codigo} - {cuenta.nombre}
                      </MenuItem>
                    ))}
                  </Select>
                  <Select value={apunte.tipo} onChange={(e) => actualizarApunte(indice, 'tipo', e.target.value as 'debe' | 'haber')} sx={{ flex: 1, minWidth: 120 }}>
                    <MenuItem value="debe">Debe</MenuItem>
                    <MenuItem value="haber">Haber</MenuItem>
                  </Select>
                  <TextField label="Importe" value={apunte.importe} onChange={(e) => actualizarApunte(indice, 'importe', e.target.value)} required sx={{ flex: 1, minWidth: 120 }} />
                  <IconButton onClick={() => eliminarApunte(indice)} disabled={apuntes.length <= 2}>
                    <DeleteIcon />
                  </IconButton>
                </Stack>
              ))}
            </Stack>
            <Button startIcon={<AddIcon />} onClick={anadirApunte} variant="outlined">
              Añadir apunte
            </Button>
            {error && <Alert severity="error">{error}</Alert>}
            <Button type="submit" variant="contained" disabled={guardando}>
              Guardar asiento
            </Button>
          </Stack>
        </Paper>
      )}

      <Paper component="section" elevation={1} sx={{ p: 3 }}>
        <Typography variant="h5" component="h2" gutterBottom>
          Asientos registrados
        </Typography>
        {asientos.length === 0 ? (
          <Typography color="text.secondary">No hay asientos registrados en este contexto.</Typography>
        ) : (
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Nº</TableCell>
                  <TableCell>Fecha</TableCell>
                  <TableCell>Concepto</TableCell>
                  <TableCell>Apuntes</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {asientos.map((asiento) => (
                  <TableRow key={asiento.id}>
                    <TableCell>{asiento.numero_asiento}</TableCell>
                    <TableCell>{asiento.fecha}</TableCell>
                    <TableCell>{asiento.concepto}</TableCell>
                    <TableCell>
                      {asiento.apuntes.map((apunte) => (
                        <Typography key={apunte.id} variant="body2">
                          {apunte.tipo.toUpperCase()} {apunte.importe}
                        </Typography>
                      ))}
                    </TableCell>
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

export default AsientosPage

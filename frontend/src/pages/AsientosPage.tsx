import { useCallback, useEffect, useRef, useState } from 'react'
import type { ChangeEvent, FormEvent } from 'react'
import AddIcon from '@mui/icons-material/Add'
import AttachFileIcon from '@mui/icons-material/AttachFile'
import DeleteIcon from '@mui/icons-material/Delete'
import DownloadIcon from '@mui/icons-material/Download'
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

type Documento = {
  id: string
  nombre: string
  tipo_contenido: string
  tamano: number
  creado_en: string
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
  documentos: Documento[]
}

type ApunteFormulario = {
  cuenta_id: string
  tipo: 'debe' | 'haber'
  importe: string
}

type ArchivoSeleccionado = { archivo: File; clave: string }

const TIPOS_ADMITIDOS = ['application/pdf', 'image/jpeg', 'image/png']
const EXTENSIONES_ADMITIDAS = ['.pdf', '.jpg', '.jpeg', '.png']
const LIMITE_ARCHIVO = 10 * 1024 * 1024

function claveUnica() {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
    return crypto.randomUUID()
  }
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`
}

function identidadArchivo(archivo: File) {
  return `${archivo.name}|${archivo.size}|${archivo.lastModified}`
}

function extensionDe(nombre: string) {
  const punto = nombre.lastIndexOf('.')
  return punto === -1 ? '' : nombre.slice(punto).toLowerCase()
}

function detalleError(fallo: unknown) {
  if (axios.isAxiosError(fallo)) {
    const detalle = fallo.response?.data?.detail
    if (typeof detalle === 'string') return detalle
    if (Array.isArray(detalle)) {
      return detalle
        .map((item) => (typeof item?.msg === 'string' ? item.msg : ''))
        .filter(Boolean)
        .join(', ')
    }
  }
  return ''
}

async function subirArchivos(asientoId: string, items: ArchivoSeleccionado[]) {
  const fallidos: ArchivoSeleccionado[] = []
  const errores: string[] = []
  for (const item of items) {
    const formulario = new FormData()
    formulario.append('archivos', item.archivo)
    formulario.append('clave_idempotencia', item.clave)
    try {
      await cliente.post(`/asientos/${asientoId}/documentos`, formulario)
    } catch (fallo) {
      fallidos.push(item)
      const detalle = detalleError(fallo)
      errores.push(detalle ? `${item.archivo.name}: ${detalle}` : `${item.archivo.name}: no se pudo subir`)
    }
  }
  return { fallidos, errores }
}

async function descargarDocumento(asientoId: string, documento: Documento) {
  const { data } = await cliente.get(`/asientos/${asientoId}/documentos/${documento.id}/descarga`, {
    responseType: 'blob',
  })
  const url = URL.createObjectURL(data)
  const enlace = document.createElement('a')
  enlace.href = url
  enlace.download = documento.nombre
  document.body.appendChild(enlace)
  enlace.click()
  enlace.remove()
  setTimeout(() => URL.revokeObjectURL(url), 1000)
}

function validarArchivos(seleccionados: File[], existentes: File[] = []) {
  const validos: File[] = []
  const rechazados: string[] = []
  const vistos = new Set(existentes.map(identidadArchivo))
  seleccionados.forEach((archivo) => {
    const identidad = identidadArchivo(archivo)
    const tipoValido =
      TIPOS_ADMITIDOS.includes(archivo.type) || EXTENSIONES_ADMITIDAS.includes(extensionDe(archivo.name))
    if (vistos.has(identidad)) {
      rechazados.push(`${archivo.name}: ya está en la lista`)
    } else if (!tipoValido) {
      rechazados.push(`${archivo.name}: formato no admitido`)
    } else if (archivo.size === 0) {
      rechazados.push(`${archivo.name}: está vacío`)
    } else if (archivo.size > LIMITE_ARCHIVO) {
      rechazados.push(`${archivo.name}: supera los 10 MB`)
    } else {
      vistos.add(identidad)
      validos.push(archivo)
    }
  })
  return { validos, rechazados }
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
  const [errorListado, setErrorListado] = useState('')
  const [exito, setExito] = useState('')
  const [guardando, setGuardando] = useState(false)
  const [archivos, setArchivos] = useState<ArchivoSeleccionado[]>([])
  const [errorArchivos, setErrorArchivos] = useState('')
  const [avisoSubida, setAvisoSubida] = useState('')
  const [pendienteReintento, setPendienteReintento] = useState<{
    asientoId: string
    archivos: ArchivoSeleccionado[]
  } | null>(null)
  const [reintentando, setReintentando] = useState(false)
  const [asientoParaAdjuntar, setAsientoParaAdjuntar] = useState<string | null>(null)
  const [subiendoAdjuntos, setSubiendoAdjuntos] = useState(false)
  const [avisoAdjuntos, setAvisoAdjuntos] = useState<{ severidad: 'success' | 'warning' | 'error'; texto: string } | null>(
    null,
  )
  const inputAdjuntos = useRef<HTMLInputElement>(null)
  const enviando = useRef(false)
  const contextoAlAdjuntar = useRef<{ entidadId: string | null | undefined; ejercicioId: string | null | undefined } | null>(
    null,
  )

  const contextoActual = useRef({ entidadId: entidadSeleccionadaId, ejercicioId: ejercicioSeleccionadoId })
  const generacionCuentas = useRef(0)
  const generacionAsientos = useRef(0)

  useEffect(() => {
    contextoActual.current = { entidadId: entidadSeleccionadaId, ejercicioId: ejercicioSeleccionadoId }
  }, [entidadSeleccionadaId, ejercicioSeleccionadoId])

  const cargarCuentas = useCallback(async () => {
    const { entidadId } = contextoActual.current
    if (!entidadId) return
    const generacion = ++generacionCuentas.current
    try {
      const { data } = await cliente.get<Cuenta[]>('/cuentas', { params: { entidad_id: entidadId } })
      if (generacion !== generacionCuentas.current || contextoActual.current.entidadId !== entidadId) return
      setCuentas(data)
    } catch {
      if (generacion === generacionCuentas.current) setCuentas([])
    }
  }, [])

  const cargarAsientos = useCallback(async () => {
    const { entidadId, ejercicioId } = contextoActual.current
    if (!entidadId || !ejercicioId) return
    const generacion = ++generacionAsientos.current
    try {
      const { data } = await cliente.get<Asiento[]>('/asientos', {
        params: { entidad_id: entidadId, ejercicio_id: ejercicioId },
      })
      if (
        generacion !== generacionAsientos.current ||
        contextoActual.current.entidadId !== entidadId ||
        contextoActual.current.ejercicioId !== ejercicioId
      ) {
        return
      }
      setAsientos(data)
      setErrorListado('')
    } catch {
      if (generacion === generacionAsientos.current) setErrorListado('No se pudo cargar el listado de asientos')
    }
  }, [])

  useEffect(() => {
    setCuentas([])
    void cargarCuentas()
  }, [entidadSeleccionadaId, cargarCuentas])

  useEffect(() => {
    setAsientos([])
    setApuntes([
      { cuenta_id: '', tipo: 'debe', importe: '' },
      { cuenta_id: '', tipo: 'haber', importe: '' },
    ])
    setError('')
    setErrorListado('')
    setExito('')
    setArchivos([])
    setErrorArchivos('')
    setAvisoSubida('')
    setPendienteReintento(null)
    setReintentando(false)
    setAvisoAdjuntos(null)
    setAsientoParaAdjuntar(null)
    setSubiendoAdjuntos(false)
    contextoAlAdjuntar.current = null
    void cargarAsientos()
  }, [entidadSeleccionadaId, ejercicioSeleccionadoId, cargarAsientos])

  const puedeCrear = usuario?.rol.nombre === 'administrador' || usuario?.rol.nombre === 'tesorero'

  const sigueElContexto = (contexto: { entidadId: string | null | undefined; ejercicioId: string | null | undefined }) =>
    contextoActual.current.entidadId === contexto.entidadId &&
    contextoActual.current.ejercicioId === contexto.ejercicioId

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

  const seleccionarArchivos = (evento: ChangeEvent<HTMLInputElement>) => {
    const seleccionados = Array.from(evento.target.files ?? [])
    evento.target.value = ''
    const { validos, rechazados } = validarArchivos(
      seleccionados,
      archivos.map((item) => item.archivo),
    )
    setArchivos((actuales) => [...actuales, ...validos.map((archivo) => ({ archivo, clave: claveUnica() }))])
    setErrorArchivos(rechazados.join('. '))
  }

  const abrirAdjuntos = (asientoId: string) => {
    setAsientoParaAdjuntar(asientoId)
    contextoAlAdjuntar.current = { ...contextoActual.current }
    inputAdjuntos.current?.click()
  }

  const adjuntarAExistente = async (evento: ChangeEvent<HTMLInputElement>) => {
    const seleccionados = Array.from(evento.target.files ?? [])
    evento.target.value = ''
    const asientoId = asientoParaAdjuntar
    const contextoInicial = contextoAlAdjuntar.current ?? { ...contextoActual.current }
    contextoAlAdjuntar.current = null
    setAsientoParaAdjuntar(null)
    if (!asientoId) return
    if (!sigueElContexto(contextoInicial)) {
      setAvisoAdjuntos({
        severidad: 'warning',
        texto: 'La entidad o el ejercicio cambió; vuelve a adjuntar los documentos.',
      })
      return
    }

    const { validos, rechazados } = validarArchivos(seleccionados)
    if (validos.length === 0) {
      setAvisoAdjuntos({ severidad: 'warning', texto: rechazados.join('. ') || 'No se eligió ningún archivo' })
      return
    }

    setSubiendoAdjuntos(true)
    try {
      const items = validos.map((archivo) => ({ archivo, clave: claveUnica() }))
      const { fallidos, errores } = await subirArchivos(asientoId, items)
      if (!sigueElContexto(contextoInicial)) return
      const mensajes = [...rechazados, ...errores]
      if (fallidos.length > 0) {
        mensajes.push(`No se pudieron adjuntar ${fallidos.length} de ${items.length} documentos`)
      }
      if (mensajes.length === 0) {
        setAvisoAdjuntos({ severidad: 'success', texto: 'Documentos adjuntados correctamente' })
      } else {
        setAvisoAdjuntos({ severidad: 'warning', texto: mensajes.join('. ') })
      }
      await cargarAsientos()
    } catch {
      if (sigueElContexto(contextoInicial)) {
        setAvisoAdjuntos({ severidad: 'error', texto: 'No se pudieron adjuntar los documentos' })
      }
    } finally {
      setSubiendoAdjuntos(false)
    }
  }

  const descargar = async (asientoId: string, documento: Documento) => {
    try {
      await descargarDocumento(asientoId, documento)
      setAvisoAdjuntos(null)
    } catch {
      setAvisoAdjuntos({
        severidad: 'error',
        texto: `No se pudo descargar «${documento.nombre}». Inténtalo de nuevo.`,
      })
    }
  }

  const quitarArchivo = (indice: number) => {
    setArchivos((actuales) => actuales.filter((_, i) => i !== indice))
  }

  const quitarPendiente = (clave: string) => {
    if (!pendienteReintento) return
    const restantes = pendienteReintento.archivos.filter((item) => item.clave !== clave)
    if (restantes.length === 0) {
      setPendienteReintento(null)
      setAvisoSubida('')
    } else {
      setPendienteReintento({ ...pendienteReintento, archivos: restantes })
    }
  }

  const reintentarSubida = async () => {
    if (!pendienteReintento || reintentando) return
    const contextoInicial = { ...contextoActual.current }
    const pendiente = pendienteReintento
    setReintentando(true)
    setAvisoSubida('')
    try {
      const { fallidos, errores } = await subirArchivos(pendiente.asientoId, pendiente.archivos)
      if (!sigueElContexto(contextoInicial)) return
      if (fallidos.length === 0) {
        setPendienteReintento(null)
        setExito('Documentos adjuntados correctamente')
      } else {
        setPendienteReintento({ ...pendiente, archivos: fallidos })
        setAvisoSubida(
          `No se pudieron adjuntar todos los documentos. ${errores.join('. ') || 'Revisa los archivos e inténtalo de nuevo.'}`,
        )
      }
      await cargarAsientos()
    } finally {
      setReintentando(false)
    }
  }

  const crear = async (evento: FormEvent) => {
    evento.preventDefault()
    if (enviando.current) return
    if (!entidadSeleccionadaId || !ejercicioSeleccionadoId) {
      setError('Selecciona una entidad y un ejercicio en la cabecera.')
      return
    }
    enviando.current = true
    const contextoInicial = { ...contextoActual.current }
    setError('')
    setExito('')
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
      const { data } = await cliente.post<Asiento>('/asientos', payload)
      const adjuntos = archivos
      if (!sigueElContexto(contextoInicial)) {
        if (adjuntos.length > 0) await subirArchivos(data.id, adjuntos)
        return
      }
      setConcepto('')
      setDescripcion('')
      setApuntes([
        { cuenta_id: '', tipo: 'debe', importe: '' },
        { cuenta_id: '', tipo: 'haber', importe: '' },
      ])
      setArchivos([])
      setErrorArchivos('')
      setExito('Asiento guardado correctamente')
      if (adjuntos.length > 0) {
        setAvisoSubida('')
        setPendienteReintento(null)
        const { fallidos, errores } = await subirArchivos(data.id, adjuntos)
        if (!sigueElContexto(contextoInicial)) return
        if (fallidos.length === 0) {
          setExito('Asiento guardado con sus documentos')
        } else {
          setPendienteReintento({ asientoId: data.id, archivos: fallidos })
          const resumen =
            fallidos.length === adjuntos.length
              ? 'El asiento se guardó, pero no se pudieron adjuntar los documentos.'
              : `El asiento se guardó, pero ${fallidos.length} de ${adjuntos.length} documentos no se pudieron adjuntar.`
          setAvisoSubida(`${resumen} ${errores.join('. ')}`.trim())
        }
      }
      await cargarAsientos()
    } catch (fallo) {
      if (sigueElContexto(contextoInicial)) {
        const detalle = axios.isAxiosError(fallo) ? fallo.response?.data?.detail : undefined
        if (typeof detalle === 'string') {
          setError(detalle)
        } else if (Array.isArray(detalle)) {
          setError(detalle.map((d: any) => d.msg).join(', '))
        } else {
          setError('No se pudo crear el asiento')
        }
      }
    } finally {
      enviando.current = false
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
            <Stack spacing={1}>
              <Typography variant="subtitle1">Documentos justificativos</Typography>
              <Button variant="outlined" component="label" startIcon={<AttachFileIcon />} sx={{ alignSelf: 'flex-start' }}>
                Adjuntar facturas o recibos
                <input type="file" hidden multiple accept=".pdf,.jpg,.jpeg,.png" onChange={seleccionarArchivos} />
              </Button>
              <Typography variant="body2" color="text.secondary">
                PDF, JPG o PNG de hasta 10 MB por archivo.
              </Typography>
              {archivos.map((item, indice) => (
                <Stack key={item.clave} direction="row" spacing={1} sx={{ alignItems: 'center' }}>
                  <Typography variant="body2">{item.archivo.name}</Typography>
                  <IconButton size="small" aria-label={`Quitar ${item.archivo.name}`} onClick={() => quitarArchivo(indice)}>
                    <DeleteIcon fontSize="small" />
                  </IconButton>
                </Stack>
              ))}
              {errorArchivos && <Alert severity="warning">{errorArchivos}</Alert>}
            </Stack>
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
            {exito && <Alert severity="success">{exito}</Alert>}
            {avisoSubida && (
              <Alert
                severity="warning"
                action={
                  pendienteReintento ? (
                    <Button color="inherit" size="small" onClick={reintentarSubida} disabled={reintentando}>
                      {reintentando ? 'Adjuntando…' : 'Reintentar'}
                    </Button>
                  ) : undefined
                }
              >
                {avisoSubida}
              </Alert>
            )}
            {pendienteReintento && pendienteReintento.archivos.length > 0 && (
              <Stack spacing={1}>
                <Typography variant="body2" color="text.secondary">
                  Documentos pendientes de adjuntar:
                </Typography>
                {pendienteReintento.archivos.map((item) => (
                  <Stack key={item.clave} direction="row" spacing={1} sx={{ alignItems: 'center' }}>
                    <Typography variant="body2">{item.archivo.name}</Typography>
                    <IconButton
                      size="small"
                      aria-label={`Descartar ${item.archivo.name}`}
                      onClick={() => quitarPendiente(item.clave)}
                      disabled={reintentando}
                    >
                      <DeleteIcon fontSize="small" />
                    </IconButton>
                  </Stack>
                ))}
              </Stack>
            )}
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
        <input
          ref={inputAdjuntos}
          type="file"
          hidden
          multiple
          accept=".pdf,.jpg,.jpeg,.png"
          onChange={adjuntarAExistente}
        />
        {avisoAdjuntos && (
          <Alert severity={avisoAdjuntos.severidad} sx={{ mb: 2 }}>
            {avisoAdjuntos.texto}
          </Alert>
        )}
        {errorListado && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {errorListado}
          </Alert>
        )}
        {errorListado ? null : asientos.length === 0 ? (
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
                  <TableCell>Documentos</TableCell>
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
                    <TableCell>
                      {asiento.documentos.length === 0 && !puedeCrear ? (
                        <Typography variant="body2" color="text.secondary">
                          —
                        </Typography>
                      ) : (
                        <Stack spacing={0}>
                          {asiento.documentos.map((documento) => (
                            <Button
                              key={documento.id}
                              size="small"
                              startIcon={<DownloadIcon />}
                              onClick={() => void descargar(asiento.id, documento)}
                              sx={{ display: 'flex', justifyContent: 'flex-start', textTransform: 'none' }}
                            >
                              {documento.nombre}
                            </Button>
                          ))}
                          {puedeCrear && (
                            <Button
                              size="small"
                              startIcon={<AttachFileIcon />}
                              disabled={subiendoAdjuntos}
                              onClick={() => abrirAdjuntos(asiento.id)}
                              aria-label={`Adjuntar documentos al asiento ${asiento.numero_asiento}`}
                              sx={{ display: 'flex', justifyContent: 'flex-start', textTransform: 'none' }}
                            >
                              Adjuntar
                            </Button>
                          )}
                        </Stack>
                      )}
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

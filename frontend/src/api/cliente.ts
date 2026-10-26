import axios from 'axios'

export const CLAVE_SESION = 'sesion'
export const EVENTO_SESION_CADUCADA = 'sesion-caducada'

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api/v1'

export const cliente = axios.create({ baseURL: API_URL })

cliente.interceptors.request.use((configuracion) => {
  const token = sessionStorage.getItem(CLAVE_SESION)
  if (token) {
    configuracion.headers.Authorization = `Bearer ${token}`
  }
  return configuracion
})

cliente.interceptors.response.use(
  (respuesta) => respuesta,
  (error) => {
    const esLogin = axios.isAxiosError(error) && error.config?.url?.includes('/auth/login')
    if (axios.isAxiosError(error) && error.response?.status === 401 && !esLogin) {
      sessionStorage.removeItem(CLAVE_SESION)
      window.dispatchEvent(new Event(EVENTO_SESION_CADUCADA))
    }
    return Promise.reject(error)
  },
)

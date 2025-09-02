import { useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { useAppDispatch, useAppSelector } from "@/store/hooks"
import { loginUser, clearError } from "@/store/slices/authSlice"
import { LoginForm, type LoginFormData } from "@/components/features/auth/login-form"

export default function LoginPage() {
  const navigate = useNavigate()
  const dispatch = useAppDispatch()
  const { isLoading, error, isAuthenticated } = useAppSelector(state => state.auth)

  // 页面级副作用：清除错误信息
  useEffect(() => {
    dispatch(clearError())
  }, [dispatch])

  // 页面级副作用：登录成功后重定向
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/', { replace: true })
    }
  }, [isAuthenticated, navigate])

  // 页面级业务逻辑：处理登录提交
  const handleSubmit = async (data: LoginFormData) => {
    console.log('LoginPage: Submitting login:', { email: data.email, password: '***' })
    dispatch(loginUser(data))
  }

  // 页面组装：将状态和逻辑传递给UI组件
  return (
    <LoginForm 
      onSubmit={handleSubmit}
      error={error}
      loading={isLoading}
    />
  )
}
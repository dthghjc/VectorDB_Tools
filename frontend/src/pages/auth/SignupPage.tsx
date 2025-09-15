import { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { useAppDispatch, useAppSelector } from "@/store/hooks"
import { registerUser, clearError } from "@/store/slices/authSlice"
import { SignupForm, type SignupFormData } from "@/components/features/auth/signup-form"

export default function SignupPage() {
  const navigate = useNavigate()
  const dispatch = useAppDispatch()
  const { isLoading, error, isAuthenticated, user } = useAppSelector(state => state.auth)
  const [registrationSuccess, setRegistrationSuccess] = useState(false)

  // 页面级副作用：清除错误信息
  useEffect(() => {
    dispatch(clearError())
  }, [dispatch])

  // 页面级副作用：如果已登录，重定向到主页
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/', { replace: true })
    }
  }, [isAuthenticated, navigate])

  // 页面级副作用：监听注册成功
  useEffect(() => {
    if (user && !isAuthenticated && !error) {
      // 注册成功但未登录（需要审核）
      setRegistrationSuccess(true)
    }
  }, [user, isAuthenticated, error])

  // 页面级业务逻辑：处理注册提交
  const handleSubmit = async (data: SignupFormData) => {
    dispatch(registerUser(data))
  }

  // 页面组装：将状态和逻辑传递给UI组件
  return (
    <SignupForm 
      onSubmit={handleSubmit}
      error={error}
      loading={isLoading}
      success={registrationSuccess}
    />
  )
}

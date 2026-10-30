import AuthForm from "../components/AuthForm";

type LoginProps = {
  onAuthenticated: () => void;
};

export default function Login({ onAuthenticated }: LoginProps) {
  return <AuthForm mode="login" onAuthenticated={onAuthenticated} />;
}

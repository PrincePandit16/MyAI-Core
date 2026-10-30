import AuthForm from "../components/AuthForm";

type RegisterProps = {
  onAuthenticated: () => void;
};

export default function Register({ onAuthenticated }: RegisterProps) {
  return <AuthForm mode="register" onAuthenticated={onAuthenticated} />;
}

import { initializeApp } from "firebase/app";
import { getAuth, GoogleAuthProvider } from "firebase/auth";

const firebaseConfig = {
  apiKey: "AIzaSyCNm9OQaiZGKV9YgfmnASgZ-VF4TxsMPac",
  authDomain: "tpv-primecolada.firebaseapp.com",
  projectId: "tpv-primecolada",
  storageBucket: "tpv-primecolada.firebasestorage.app",
  messagingSenderId: "15318690559",
  appId: "1:15318690559:web:e3ddfbe7c0a4412395baca"
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const googleProvider = new GoogleAuthProvider();

export { auth, googleProvider };
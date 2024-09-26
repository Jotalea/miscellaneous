caracteres_disponibles = "+-/*!&$#?=@abcdefghijklnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"

def generar_contrasena(longitud):
    import random
    contrasena = ''.join(random.choice(caracteres_disponibles) for _ in range(longitud))
    return contrasena

def main():
    longitud = int(input("Ingrese la longitud de la contraseña: "))
    contrasena = generar_contrasena(longitud)
    print("Contraseña generada:", contrasena)

if __name__ == "__main__":
    main()

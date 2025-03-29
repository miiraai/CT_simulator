import math
import numpy as np

#TODO dodac typy zmiennych

def get_parallel_rays(radius, pos, angle, span, num_rays):
    """
    Funkcja obliczająca współrzędne emitorów i detektorów dla zadanych parametrów

    :param radius: promień okręgu
    :param pos: środek badanego zdjęcia
    :param angle: kąt pod którym padają promienie (w równaniach oznaczany alfa)
    :param span: rozpiętość promieni (w równania oznaczana phi)
    :param num_rays: liczba emiterów oraz detektorów

    :return: ndarray współrzędnych emiterów i odpowiadających im detektorów
    """

    alpha = np.radians(angle)
    theta = np.radians(span)

    # Wektor indeksów promieni
    ray_indices = np.linspace(0, num_rays - 1, num_rays)

    # Obliczenie kątów dla detektorów i emiterów
    detector_angles = alpha - (ray_indices * theta / (num_rays - 1)) + theta / 2
    emitter_angles = alpha + np.pi - (theta / 2) + (ray_indices * theta / (num_rays - 1))

    # Obliczenie współrzędnych emiterów
    x_e = radius * np.cos(emitter_angles) + pos[0]
    y_e = radius * np.sin(emitter_angles) + pos[1]

    # Obliczenie współrzędnych detektorów
    x_d = radius * np.cos(detector_angles) + pos[0]
    y_d = radius * np.sin(detector_angles) + pos[1]

    # Łączenie współrzędnych w jedną tablicę: dla każdego promienia
    # element = [[x_det, x_em], [y_det, y_em]]
    rays = np.empty((num_rays, 2, 2))
    rays[:, 0, 0] = x_e
    rays[:, 0, 1] = x_d
    rays[:, 1, 0] = y_e
    rays[:, 1, 1] = y_d

    return rays

def get_bresenham_points(x1, x2, y1, y2):
    """
    Funkcja obliczająca współrzędne promieni na podstawie algorytmu Bresenhama

    :param x1: - współrzędne x emitera
    :param x2: - współrzędne x detektora
    :param y1: - współrzędne y emitera
    :param y2: - współrzędne y detektora

    :return: lista punktów odpowiadających wiązce
    """
    # floaty -> inty
    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
    dx = x2 - x1
    dy = y2 - y1

    # Określenie wiodącej osi
    is_steep = abs(dy) > abs(dx)

    # Jeżeli OY jest wiodąca odwracamy współrzędne inaczej dzielenie przez 0 przy kącie prostym
    if is_steep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2

    # Jeżeli współrzędne są odwrócone to zamieniamy na potrzeby obliczeń
    swapped = False
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
        swapped = True

    # Obliczenie delt jeszcze raz po posprzątaniu inputu
    dx = x2 - x1
    dy = y2 - y1

    # Obliczenie błędu
    error = int(dx / 2.0)
    ystep = 1 if y1 < y2 else -1

    y = y1
    points = []
    for x in range(x1, x2 + 1):
        coord = (y, x) if is_steep else (x, y)
        points.append(coord)
        error -= abs(dy)
        if error < 0:
            y += ystep
            error += dx

    # Odwrócenie współrzędnych punktów jeżeli były w złej kolejności na potrzeby obliczeń
    if swapped:
        points.reverse()
    return points

def calculate_sinogram(img, steps, span, num_rays, max_angle):
    """
    Funkcja obliczająca sinogram obrazu wejściowego

    :param img: - ndarray obrazu wejściowego
    :param steps: - ilość kroków (emiterów oraz detektorów)
    :param span: - zakres promieni
    :param num_rays: - liczba promieni
    :param max_angle: - maksymalny kąt

    :return ndarray odpowiadający sinogramowi
    """
    # Pusty ndarray wypełniany dalej sinogramem (czarny obraz)
    sinogram = np.zeros((steps, num_rays))
    for idx in range(steps):
        # Kąt padania promieni i współrzędne emiterów oraz detektorów
        angle = idx * (max_angle/steps)
        rays = get_parallel_rays(max(img.shape[0]//2, img.shape[1]//2) * np.sqrt(2),
                                 (img.shape[0]//2, img.shape[1]//2), angle, span, num_rays)
        for ray_idx, ray in enumerate(rays):
            # Współrzędne wiązek z emiterów
            emitter_value = 0
            points = get_bresenham_points(ray[0][0], ray[0][1], ray[1][0], ray[1][1])
            for point in points:
                # Rozświetlanie pikseli w granicach obrazu
                if (0 <= point[0] < img.shape[0]) and (0 <= point[1] < img.shape[1]):
                    emitter_value += img[point[0]][point[1]]
            sinogram[idx][ray_idx] = emitter_value
    # Transponujemy ponieważ format odpowiada formatowi danych zbieranych przez rzeczywisty
    # tomograf (każdy wiersz to wyniki uzyskane dla danego kąta), który powodowałby błędne
    # wykreślenie sinogramu
    return sinogram

def reverse_radon_transform(img, sinogram, steps=60, span=120, num_rays=250, max_angle=180):
    """
    Funkcja uzyskująca rekonstrukcję oryginalnego obrazu na podstawie sinogramu używając
    odwróconej transformaty Radona

    :param img: - ndarray obrazu wejściowego
    :param sinogram: - sinogram wejściowy
    :param steps: - ilość kroków (emiterów oraz detektorów)
    :param span: - zakres promieni
    :param num_rays: - liczba promieni
    :param max_angle: - maksymalny kąt

    :return: ndarray przedstawiąjący zrekonstruowany obraz wejściowy
    """
    out_image = np.zeros((img.shape[0], img.shape[1]))

    for idx in range(steps):
        angle = idx * max_angle / steps
        rays = get_parallel_rays(max(img.shape[0] // 2, img.shape[1] // 2) * np.sqrt(2),
                                 (img.shape[0] // 2, img.shape[1] // 2), angle, span, num_rays)
        for ray_idx, ray in enumerate(rays):
            points = get_bresenham_points(ray[0][0], ray[0][1], ray[1][0], ray[1][1])
            for point in points:
                # Tylko dla punktów zawierających się w sinogramie
                if (0 <= point[0] < img.shape[0]) and (0 <= point[1] < img.shape[1]):
                    out_image[point[0]][point[1]] += sinogram[idx][ray_idx]

    return out_image

def create_kernel(size, kernel_type):
    """
    Tworzenie kernela w zależności od podanej wielkości i typu.
    Dopuszczalne typy to: rampowy (Ram-Lak), Shepp-Logan, Cosine, Hamming, Hann

    :param size: wielkość kernela
    :param kernel_type: typ kernela

    :return: wyjściowy kernel o danym size i type
    """
    kernel = np.zeros(size, dtype=np.float64)
    kernel_center = len(kernel) // 2

    match kernel_type:
        case 'ramp':
            for i in range(size):
                if i == kernel_center:
                    kernel[i] = 1.0
                elif i % 2 == 0:
                    kernel[i] = 0.0
                else:
                    dist = i - kernel_center
                    kernel[i] = (-4.0 / (math.pi ** 2)) / (dist ** 2)
        case 'shepp-logan':
            for i in range(size):
                if i == kernel_center:
                    kernel[i] = 1.0
                elif i % 2 == 0:
                    kernel[i] = 0.0
                else:
                    dist = i - kernel_center
                    sinc = math.sin(math.pi * dist / (2 * kernel_center)) / (math.pi * dist / (2 * kernel_center))
                    kernel[i] = (-4.0 / (math.pi ** 2)) / (dist ** 2) * sinc
        case 'hamming':
            for i in range(size):
                if i == kernel_center:
                    kernel[i] = 1.0
                elif i % 2 == 0:
                    kernel[i] = 0.0
                else:
                    dist = i - kernel_center
                    window = 0.54 - 0.46 * math.cos(2 * math.pi * i / (size - 1))
                    kernel[i] = (-4.0 / (math.pi ** 2)) / (dist ** 2) * window
        case 'hanning':
            for i in range(size):
                if i == kernel_center:
                    kernel[i] = 1.0
                elif i % 2 == 0:
                    kernel[i] = 0.0
                else:
                    dist = i - kernel_center
                    window = 0.5 * (1 - math.cos(2 * math.pi * i / (size - 1)))
                    kernel[i] = (-4.0 / (math.pi ** 2)) / (dist ** 2) * window
        case _:
            raise ValueError("No such kernel type")

    return kernel


def convolve_sinogram(sinogram, kernel):
    """
    Dokonuje konwolucji każdego wiersza (projekcji) sinogramu z podanym jądrem

    :param sinogram: macierz sinogramu
    :param kernel: 1D jądro filtra

    :return: ndarray przefiltrowanego sinogramu
    """
    width, height = sinogram.shape
    out = np.zeros_like(sinogram)
    for i in range(width):
        # mode='same' - wynik tej samej długości co wejście
        out[i, :] = np.convolve(sinogram[i, :], kernel, mode='same')
    return out
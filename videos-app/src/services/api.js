import { S3Client, GetObjectCommand, ListObjectsV2Command, PutObjectCommand } from "@aws-sdk/client-s3";
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";


const S3_BUCKET_NAME = import.meta.env.VITE_S3_BUCKET_NAME;
const REGION = import.meta.env.VITE_AWS_REGION;
const BASE_URL = ''; //import.meta.env.VITE_BASE_URL;

console.log(S3_BUCKET_NAME, REGION, BASE_URL);

const s3 = new S3Client({
    region: REGION,
    credentials: {
        accessKeyId: import.meta.env.VITE_AWS_ACCESS_KEY_ID,
        secretAccessKey: import.meta.env.VITE_AWS_SECRET_ACCESS_KEY,
    },
});

const API_URL = `${BASE_URL}/api/ai/process-videos`;
const INVERTED_INDEX_URL = `${BASE_URL}/api/index/`;

const fetchFromProcessor = async (videoTitle, videoFileName) => {
    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                title: videoTitle,
                fileName: 'videos/' + videoFileName,
            }),
        });

        if (!response.ok) {
            throw new Error('Error en la comunicación con el servicio Processor');
        }

        console.log("Enviado mensaje a ai");
        return await response.json();
    } catch (error) {
        console.error(error);
        throw error;
    }
};

const fetchFromInvertedIndex = async (query) => {
    try {
        const params = new URLSearchParams({'query': query});
        console.log(`${INVERTED_INDEX_URL}?${params.toString()}`)
        const response = await fetch(`${INVERTED_INDEX_URL}?${params.toString()}`);
        if (!response.ok) {
            throw new Error(`Error en la comunicación con el servicio Inverted Index: ${response.status}`);
        }
        const data = await response.json();
        console.log('InvertedIndex:', response)
        console.log('InvertedIndex:', data)
        return data;
    } catch (error) {
        console.error(error);
        throw error;
    }
};

const fetchFromS3 = async (fileName) => {
    try {
        const params = {
            Bucket: S3_BUCKET_NAME,
            Key: fileName,
        };
        const command = new GetObjectCommand(params);
        const data = await s3.send(command);
        return data.Body;
    } catch (error) {
        console.error(error);
        throw error;
    }
};

const listFilesFromS3 = async () => {
    const targetPrefix = 'videos/';
    try {
        const params = {
            Bucket: `${S3_BUCKET_NAME}`,
            Prefix: 'videos/',
        };
        const command = new ListObjectsV2Command(params);
        const data = await s3.send(command);
        const files = data.Contents.map(item => item.Key);
        const filteredKeys = files.filter(key => key !== targetPrefix);
        return filteredKeys;
    } catch (error) {
        console.error(error);
        throw error;
    }
};

const PRESIGNED_URL_EXPIRATION = 3600;

export const generatePresignedUrlForKey = async (key) => {
    const command = new GetObjectCommand({
        Bucket: S3_BUCKET_NAME,
        Key: key,
    });

    try {
        const url = await getSignedUrl(s3, command, {
            expiresIn: PRESIGNED_URL_EXPIRATION,
        });
        return url;
    } catch (error) {
        console.error(`Error al generar URL prefirmada para la clave ${key}:`, error);
        throw new Error(`No se pudo generar la URL para ${key}`);
    }
};



const uploadToS3 = async (file, fileName) => {
    console.log('Objeto file recibido:', file); // Para ver toda la estructura
    console.log('Tipo de archivo (file.type):', file.type); // Usar file.type
    console.log('Tamaño del archivo (file.size):', file.size);

    console.log(file.type);

    try {
        const arrayBuffer = await file.arrayBuffer();
        const params = {
            Bucket: `${S3_BUCKET_NAME}`,
            Key: `videos/${fileName}`,
            Body: arrayBuffer,
            ContentType: file.type,
        };
        const command = new PutObjectCommand(params);
        console.log("Enviando comando a S3 con stream...");
        const result = await s3.send(command);
        console.log("Resultado de S3:", result);
        console.log("Archivo subido exitosamente a S3");
    } catch (error) {
        console.error("Error subiendo a S3:", error);
        if (error.name === 'TypeError' && error.message.includes('getReader')) {
            console.error("El error de getReader persiste. Verifica la compatibilidad del navegador o la versión del SDK.");
        }
        throw error;
    }
};

export { fetchFromProcessor, fetchFromInvertedIndex, fetchFromS3, uploadToS3, listFilesFromS3 };

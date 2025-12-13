import { useState } from "react";
import Service from "../../service/Service.js";

export default function CargaMasiva() {
	const [file, setFile] = useState(null);
	const [isUploading, setIsUploading] = useState(false);
	const [alert, setAlert] = useState(null); // { type: 'success' | 'error', message: string }
    const [serviceStatus, setServiceStatus] = useState(null); // { ok: boolean, detail?: string }

	const onFileChange = (e) => {
		const f = e.target.files?.[0] || null;
		setFile(f);
		setAlert(null);
	};

	const onDrop = (e) => {
		e.preventDefault();
		const f = e.dataTransfer.files?.[0] || null;
		if (f) {
			setFile(f);
			setAlert(null);
		}
	};

	const onDragOver = (e) => {
		e.preventDefault();
	};

	const checkHealth = async () => {
		try {
			const data = await Service.health();
			setServiceStatus({ ok: data?.status === "ok" });
		} catch (err) {
			setServiceStatus({ ok: false, detail: err?.error || "Backend no disponible" });
		}
	};

	const uploadFile = async () => {
		if (!file) {
			setAlert({ type: "error", message: "Selecciona un archivo CSV antes de subir." });
			return;
		}
		if (!file.name.toLowerCase().endsWith(".csv")) {
			setAlert({ type: "error", message: "Solo se permiten archivos con extensión .csv." });
			return;
		}

		try {
			setIsUploading(true);
			setAlert(null);
			const data = await Service.cargaMasiva(file);
			setAlert({ type: "success", message: data?.message || "Archivo subido exitosamente." });
		} catch (err) {
			const msg = typeof err === "string" ? err : (err?.error || err?.message || "Ocurrió un error al subir.");
			setAlert({ type: "error", message: msg });
		} finally {
			setIsUploading(false);
		}
	};

	return (
		<div className="w-full px-2 md:px-6 py-6">
			<div className="min-h-[70vh] bg-slate-800/50 rounded-2xl shadow-inner border border-slate-700 p-6">
				<h1 className="text-2xl font-semibold text-white mb-4">Carga Masiva</h1>

					{/* Estado del servicio */}
					<div className="mb-4">
						<button
							onClick={checkHealth}
							type="button"
							className="inline-flex items-center rounded-md bg-sky-600 px-4 py-2 text-sm font-medium text-white hover:bg-sky-700"
						>
							Comprobar servicio
						</button>
						{serviceStatus && (
							<span className={serviceStatus.ok ? "ml-3 text-emerald-700" : "ml-3 text-rose-700"}>
								{serviceStatus.ok ? "Servicio operativo" : `Servicio no disponible${serviceStatus.detail ? `: ${serviceStatus.detail}` : ''}`}
							</span>
						)}
					</div>

					{alert && (
						<div
							className={
								alert.type === "success"
									? "mb-4 rounded-lg border border-green-200 bg-green-50 text-green-800 px-4 py-3"
									: "mb-4 rounded-lg border border-red-200 bg-red-50 text-red-800 px-4 py-3"
							}
						>
							{alert.message}
						</div>
					)}

					<div
						onDrop={onDrop}
						onDragOver={onDragOver}
						className="group relative flex flex-col items-center justify-center rounded-xl border-2 border-dashed border-slate-500 bg-slate-900/40 px-8 py-12 text-center transition-colors hover:border-slate-400"
					>
						<div className="flex items-center justify-center w-16 h-16 rounded-full bg-sky-50 group-hover:bg-sky-100 mb-3">
							<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-8 h-8 text-slate-300">
								<path d="M12 2a7 7 0 00-7 7v.586A2 2 0 003 11v6a3 3 0 003 3h12a3 3 0 003-3v-6a2 2 0 00-2-2h-.05A7 7 0 0012 2zm-1 10v3a1 1 0 102 0v-3h2l-3-3-3 3h2z" />
							</svg>
						</div>
						<p className="text-slate-200 font-medium">Arrastra tu archivo aquí</p>
						<p className="text-slate-400 text-sm">o haz clic para seleccionarlo desde tu equipo</p>

						<input
							type="file"
							accept=".csv"
							onChange={onFileChange}
							className="mt-4 cursor-pointer"
						/>

						{file && (
							<div className="mt-3 inline-flex items-center gap-2 rounded-full bg-slate-800 px-3 py-1 text-sm text-slate-200 border border-slate-700">
								<span className="inline-block w-2 h-2 rounded-full bg-slate-300" />
								{file.name}
							</div>
						)}
					</div>

					<div className="mt-6 flex flex-wrap gap-3">
						<button
							onClick={uploadFile}
							disabled={isUploading}
							className="inline-flex items-center rounded-md bg-indigo-600 px-5 py-2.5 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 disabled:opacity-60"
						>
							{isUploading ? "Subiendo..." : "Subir archivo"}
						</button>

						<button
							type="button"
							className="inline-flex items-center rounded-md bg-rose-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-rose-700"
							onClick={() => { /* pendiente: limpieza */ }}
						>
							Limpiar datos
						</button>

						<button
							type="button"
							className="inline-flex items-center rounded-md bg-emerald-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-emerald-700"
							onClick={() => { /* pendiente: entrenamiento */ }}
						>
							Entrenar modelo
						</button>
					</div>
				</div>
			</div>
	);
		
}

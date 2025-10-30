import type { Socket } from "socket.io-client";

class fileSheetUpload {
  private file: File;
  private fileSize: number;

  private totalSent: number = 0;
  private fileSocket: Socket;

  constructor(file: File) {
    // randomly picked 1MB slices,
    // I don't think this size is important for this experiment

    this.fileSocket = socketio.socket("/files");
    this.fileSocket.connect();
    this.file = file;
    this.fileSize = file.size;
  }
  async upload() {
    setTimeout(async () => {
      await this.sendFileInChunks(); // Envia o arquivo em chunks de 80KB
    }, 500);

    return this.fileSocket.id;
  }
  private async sendFileInChunks() {
    const chunkSize = 1024 * 50;
    const totalChunks = Math.ceil(this.file.size / chunkSize);
    const {
      store: { progressBarValue, sidXlsxFile },
      toast,
    } = bots.loadPlugins();

    sidXlsxFile.value = String(this.fileSocket.id);

    for (let i = 0; i < totalChunks; i++) {
      const start = i * chunkSize;
      const end = Math.min(this.file.size, start + chunkSize);

      const chunk = this.file.slice(start, end);
      const arrayBuffer = await chunk.arrayBuffer();
      const currentSize = arrayBuffer.byteLength;
      this.totalSent += currentSize;
      await new Promise<void>((resolve, reject) => {
        setTimeout(() => {
          this.fileSocket.emit(
            "add_file",
            {
              name: this.file.name,
              chunk: arrayBuffer,
              current_size: currentSize,
            },
            (err: Error | null) => {
              if (err) reject(err);
              else resolve();
            },
          );
        }, 20); // delay envio de cada chunk
      });

      // Atualiza a progressbar lentamente
      const targetProgress = Math.round((this.totalSent / this.fileSize) * 100);
      const currentProgress = progressBarValue.value;
      const step = targetProgress > currentProgress ? 1 : -1;

      while (progressBarValue.value !== targetProgress) {
        progressBarValue.value += step;
        await new Promise((r) => setTimeout(r, 20)); // delay entre cada incremento
      }

      if (end >= this.file.size) {
        toast.create({
          title: "Sucesso!",
          body: `Arquivo ${this.file.name} enviado!`,
          variant: "success",
          modelValue: 5000,
        });

        await new Promise((r) => setTimeout(r, 2000));
        progressBarValue.value = 0;

        break;
      }
    }
  }
}

export default fileSheetUpload;

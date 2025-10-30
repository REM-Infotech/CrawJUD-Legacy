import type { Socket } from "socket.io-client";

class multipleFileUpload {
  private files: File[];
  private totalSent: number = 0;
  private totalFilesSizes: number = 0;

  private fileSocket: Socket;

  constructor(files: File[]) {
    this.fileSocket = socketio.socket("/files");
    this.fileSocket.connect();

    this.files = files;
    // soma o tamanho total de todos os arquivos
    this.totalFilesSizes = this.files.reduce((acc, f) => acc + f.size, 0);
  }
  async upload() {
    const {
      store: { progressBarValue, sidUploadFiles },
      toast,
    } = bots.loadPlugins();

    sidUploadFiles.value = String(this.fileSocket.id);

    for (const file of this.files) {
      await this.sendFileInChunks(file);
    }

    toast.create({
      title: "Sucesso!",
      body: `Seus ${this.files.length} foram enviados com sucesso!`,
      variant: "success",
      modelValue: 5000,
    });

    await new Promise((r) => setTimeout(r, 2000));
    progressBarValue.value = 0;
    return this.fileSocket.id;
  }
  private async sendFileInChunks(file: File) {
    const {
      store: { progressBarValue },
      toast,
    } = bots.loadPlugins();

    const chunkSize = 1024 * 500;
    const fileSize = file.size;
    const totalChunks = Math.ceil(fileSize / chunkSize);

    for (let i = 0; i < totalChunks; i++) {
      const start = i * chunkSize;
      const end = Math.min(file.size, start + chunkSize);

      const chunk = file.slice(start, end);
      const arrayBuffer = await chunk.arrayBuffer();
      const currentSize = arrayBuffer.byteLength;

      this.totalSent += currentSize;

      await new Promise<void>((resolve, reject) => {
        setTimeout(() => {
          this.fileSocket.emit(
            "add_file",
            {
              name: file.name,
              chunk: arrayBuffer,
              current_size: currentSize,
            },
            (err: Error | null) => {
              if (err) reject(err);
              else resolve();
            },
          );
        }, 20);
      });

      // Atualiza a progressbar lentamente
      const currentProgress = progressBarValue.value;
      const targetProgress = Math.round((this.totalSent / this.totalFilesSizes) * 100);
      const step = targetProgress > currentProgress ? 1 : -1;

      while (progressBarValue.value !== targetProgress) {
        progressBarValue.value += step;
        await new Promise((r) => setTimeout(r, 20));
      }
    }
    toast.create({
      title: "Sucesso!",
      body: `Arquivo ${file.name} enviado!`,
      variant: "primary",
      modelValue: 3000,
    });
  }
}

export default multipleFileUpload;

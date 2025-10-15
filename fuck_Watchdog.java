import java.io.IOException;
import java.nio.file.*;
import java.nio.file.attribute.BasicFileAttributes;

public class FolderDeleterUltimateOptimized {

    private static final String TARGET_FOLDER_NAME = "Watchdog";
    private static final String START_DIR_PATH = "server/Anti-cheat";

    public static void main(String[] args) {
        Path startDirPath = Paths.get(START_DIR_PATH).toAbsolutePath().normalize();

        if (!Files.exists(startDirPath) || !Files.isDirectory(startDirPath)) {
            return;
        }

        try {
            Files.walkFileTree(startDirPath, new SimpleFileVisitor<Path>() {

                @Override
                public FileVisitResult preVisitDirectory(Path dir, BasicFileAttributes attrs) throws IOException {
                    if (!dir.equals(startDirPath) && dir.getFileName().toString().equals(TARGET_FOLDER_NAME)) {
                        try {
                            Files.walk(dir)
                                 .sorted((p1, p2) -> p2.compareTo(p1))
                                 .forEach(path -> {
                                     try {
                                         Files.delete(path);
                                     } catch (IOException e) {
                                     }
                                 });
                        } catch (IOException e) {
                        }
                        return FileVisitResult.SKIP_SUBTREE;
                    }
                    return FileVisitResult.CONTINUE;
                }
            });

        } catch (IOException e) {
        }
    }
}

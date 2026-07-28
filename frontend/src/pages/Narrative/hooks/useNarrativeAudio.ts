import { useState, useEffect, useRef } from "react";
import { message } from "antd";

export const useNarrativeAudio = (
    aiNarratives: Record<string, { title: string; content: string }>,
    selectedPersona: string
) => {
    const [isPlaying, setIsPlaying] = useState(false);
    const speechSynthesisRef = useRef<SpeechSynthesisUtterance | null>(null);

    const handlePlayNarrative = () => {
        // Check if speech synthesis is supported
        if (!window.speechSynthesis) {
            message.error('Text-to-speech is not supported in your browser');
            return;
        }

        if (isPlaying) {
            window.speechSynthesis.cancel();
            setIsPlaying(false);
            return;
        }

        const currentNarrative = aiNarratives[selectedPersona as keyof typeof aiNarratives];
        if (!currentNarrative) {
            message.error('No narrative available to play');
            return;
        }

        const utterance = new SpeechSynthesisUtterance(currentNarrative.content);
        utterance.rate = 1.0;
        utterance.pitch = 1.0;
        utterance.volume = 1.0;
        utterance.lang = 'en-US';

        utterance.onstart = () => {
            setIsPlaying(true);
            message.success('Playing narrative audio');
        };

        utterance.onend = () => {
            setIsPlaying(false);
        };

        utterance.onerror = (event) => {
            setIsPlaying(false);
            message.error('Stopped audio');
            console.error('Speech synthesis error:', event);
        };

        speechSynthesisRef.current = utterance;
        window.speechSynthesis.speak(utterance);
    };

    useEffect(() => {
        return () => {
            window.speechSynthesis.cancel();
        };
    }, []);

    // Stop audio when persona changes
    useEffect(() => {
        if (isPlaying) {
            window.speechSynthesis.cancel();
            setIsPlaying(false);
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [selectedPersona]);

    return { isPlaying, handlePlayNarrative };
};

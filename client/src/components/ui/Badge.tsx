interface Props {
    text: string;
    className?: string;
}

const Badge = ({ text, className = '' }: Props) => {
    return (
        <span className={`px-2 py-1 text-sm font-medium rounded-full ${className}`}>
            {text}
        </span>
    );
};

export default Badge;
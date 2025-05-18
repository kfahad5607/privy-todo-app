const sizeMap = {
    sm: 'w-4 h-4 border-2',
    md: 'w-6 h-6 border-4',
    lg: 'w-8 h-8 border-4',
    xl: 'w-10 h-10 border-4',
    '2xl': 'w-12 h-12 border-4',
    '3xl': 'w-16 h-16 border-4',
    '4xl': 'w-20 h-20 border-4'
};

interface Props {
    size?: keyof typeof sizeMap;
}


const SpinnerLoader = ({ size = 'md' }: Props) => (
    <div className="flex justify-center items-center">
        <div
            className={`${sizeMap[size]} border-blue-500 border-t-transparent rounded-full animate-spin`}
        ></div>
    </div>
);

export default SpinnerLoader;